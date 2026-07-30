# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

# This file has been modified with the assistance of IBM Bob (AI Code Assistant)
"""
Tests for CWE-295 remediation: TLS certificate verification enabled by default.

Covers:
- Config.SSL_VERIFY defaults to True and respects SSL_VERIFY env var
- AuthenticationManager defaults verify_ssl=True; suppression call removed
- get_shared_auth_manager defaults verify_ssl=True
- BaseMDMAdapter defaults verify_ssl=Config.SSL_VERIFY (True)
- verify=True is forwarded to every outbound requests.post / requests.request call
- urllib3 InsecureRequestWarning is NOT suppressed at module import
"""

import sys
import importlib
import warnings
import pytest
import urllib3
from unittest.mock import patch, Mock, call


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ok_response(json_body: dict) -> Mock:
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = json_body
    resp.raise_for_status = Mock()
    resp.headers = {}
    return resp


# ---------------------------------------------------------------------------
# 1. Config.SSL_VERIFY
# ---------------------------------------------------------------------------

class TestConfigSSLVerify:
    """Config.SSL_VERIFY reads SSL_VERIFY env var and defaults to True."""

    def test_ssl_verify_default_is_true(self, monkeypatch):
        """SSL_VERIFY env var absent → Config.SSL_VERIFY is True."""
        monkeypatch.delenv("SSL_VERIFY", raising=False)
        import config as cfg
        importlib.reload(cfg)
        assert cfg.Config.SSL_VERIFY is True

    def test_ssl_verify_explicit_true(self, monkeypatch):
        """SSL_VERIFY=true → Config.SSL_VERIFY is True."""
        monkeypatch.setenv("SSL_VERIFY", "true")
        import config as cfg
        importlib.reload(cfg)
        assert cfg.Config.SSL_VERIFY is True

    def test_ssl_verify_explicit_false(self, monkeypatch):
        """SSL_VERIFY=false → Config.SSL_VERIFY is False (opt-out for dev)."""
        monkeypatch.setenv("SSL_VERIFY", "false")
        import config as cfg
        importlib.reload(cfg)
        assert cfg.Config.SSL_VERIFY is False

    def test_ssl_verify_case_insensitive(self, monkeypatch):
        """SSL_VERIFY env var comparison is case-insensitive."""
        monkeypatch.setenv("SSL_VERIFY", "FALSE")
        import config as cfg
        importlib.reload(cfg)
        assert cfg.Config.SSL_VERIFY is False

    def test_ssl_verify_whitespace_stripped(self, monkeypatch):
        """SSL_VERIFY env var value is stripped before comparison."""
        monkeypatch.setenv("SSL_VERIFY", "  false  ")
        import config as cfg
        importlib.reload(cfg)
        assert cfg.Config.SSL_VERIFY is False


# ---------------------------------------------------------------------------
# 2. urllib3 warning suppression removed
# ---------------------------------------------------------------------------

class TestNoWarningSuppressionAtImport:
    """urllib3.disable_warnings must NOT be called when the module is imported."""

    def test_insecure_request_warning_not_suppressed(self):
        """
        Importing authentication_manager must NOT suppress InsecureRequestWarning.

        We verify this by checking that the warning category is *not* in
        urllib3's filtered-warnings list after a fresh import cycle.
        """
        # Reload the module to simulate a fresh import
        import common.auth.authentication_manager as am
        importlib.reload(am)

        # urllib3 keeps suppressed warnings in its own registry; after our fix
        # InsecureRequestWarning should NOT appear there.
        suppressed = {
            str(f.category)
            for f in warnings.filters
            if "InsecureRequestWarning" in str(f)
        }
        assert not suppressed, (
            "InsecureRequestWarning must not be suppressed — "
            f"found filter entries: {suppressed}"
        )

    def test_disable_warnings_not_called_on_import(self):
        """urllib3.disable_warnings must not be called during module import."""
        with patch("urllib3.disable_warnings") as mock_dw:
            import common.auth.authentication_manager  # noqa: F401
            importlib.reload(common.auth.authentication_manager)
            mock_dw.assert_not_called()


# ---------------------------------------------------------------------------
# 3. AuthenticationManager defaults
# ---------------------------------------------------------------------------

class TestAuthenticationManagerDefaults:
    """AuthenticationManager verify_ssl must default to True."""

    def test_default_verify_ssl_is_true(self):
        from common.auth.authentication_manager import AuthenticationManager
        am = AuthenticationManager(platform="local")
        assert am.verify_ssl is True

    def test_explicit_false_accepted(self):
        """Callers can still opt out; value must be stored faithfully."""
        from common.auth.authentication_manager import AuthenticationManager
        am = AuthenticationManager(platform="local", verify_ssl=False)
        assert am.verify_ssl is False

    def test_get_shared_auth_manager_default_verify_ssl_is_true(self):
        from common.auth.authentication_manager import (
            get_shared_auth_manager,
            invalidate_shared_auth_manager,
        )
        invalidate_shared_auth_manager()
        try:
            mgr = get_shared_auth_manager()
            assert mgr.verify_ssl is True
        finally:
            invalidate_shared_auth_manager()


# ---------------------------------------------------------------------------
# 4. BaseMDMAdapter defaults
# ---------------------------------------------------------------------------

class TestBaseMDMAdapterDefaults:
    """BaseMDMAdapter verify_ssl must default to Config.SSL_VERIFY (True)."""

    def setup_method(self):
        from common.auth.authentication_manager import invalidate_shared_auth_manager
        invalidate_shared_auth_manager()

    def teardown_method(self):
        from common.auth.authentication_manager import invalidate_shared_auth_manager
        invalidate_shared_auth_manager()

    def test_adapter_default_verify_ssl_is_true(self):
        from common.core.base_adapter import BaseMDMAdapter
        adapter = BaseMDMAdapter()
        assert adapter.verify_ssl is True

    def test_adapter_propagates_verify_ssl_to_auth_manager(self):
        """verify_ssl passed to adapter must reach the shared auth manager."""
        from common.auth.authentication_manager import invalidate_shared_auth_manager
        from common.core.base_adapter import BaseMDMAdapter

        invalidate_shared_auth_manager()
        adapter = BaseMDMAdapter(verify_ssl=True)
        assert adapter._auth_manager.verify_ssl is True

    def test_adapter_explicit_false_propagates(self):
        from common.auth.authentication_manager import invalidate_shared_auth_manager
        from common.core.base_adapter import BaseMDMAdapter

        invalidate_shared_auth_manager()
        adapter = BaseMDMAdapter(verify_ssl=False)
        assert adapter.verify_ssl is False
        assert adapter._auth_manager.verify_ssl is False


# ---------------------------------------------------------------------------
# 5. verify=True forwarded to every outbound HTTP call
# ---------------------------------------------------------------------------

class TestVerifyForwardedToRequests:
    """Every outbound requests call must receive verify=True by default."""

    def setup_method(self):
        from common.auth.authentication_manager import invalidate_shared_auth_manager
        invalidate_shared_auth_manager()

    def teardown_method(self):
        from common.auth.authentication_manager import invalidate_shared_auth_manager
        invalidate_shared_auth_manager()

    @patch("common.auth.authentication_manager.requests.post")
    def test_cpd_token_fetch_uses_verify_true(self, mock_post):
        """_fetch_cpd_token must pass verify=True to requests.post."""
        import jwt
        from datetime import datetime, timedelta
        from common.auth.authentication_manager import AuthenticationManager

        exp = int((datetime.now() + timedelta(hours=1)).timestamp())
        token = jwt.encode({"exp": exp}, "", algorithm="none")
        mock_post.return_value = _make_ok_response({"token": token})

        am = AuthenticationManager(platform="cpd", verify_ssl=True)
        am._fetch_cpd_token()

        _, kwargs = mock_post.call_args
        assert kwargs.get("verify") is True

    @patch("common.auth.authentication_manager.requests.post")
    def test_cloud_token_fetch_uses_verify_true(self, mock_post):
        """_fetch_cloud_token must pass verify=True to requests.post."""
        from common.auth.authentication_manager import AuthenticationManager

        mock_post.return_value = _make_ok_response(
            {"access_token": "tok", "expires_in": 3600}
        )

        am = AuthenticationManager(platform="cloud", verify_ssl=True)
        am._fetch_cloud_token()

        _, kwargs = mock_post.call_args
        assert kwargs.get("verify") is True

    @patch("common.auth.authentication_manager.requests.post")
    def test_cpd_token_fetch_uses_verify_false_when_opted_out(self, mock_post):
        """When verify_ssl=False is explicit, requests.post must receive verify=False."""
        import jwt
        from datetime import datetime, timedelta
        from common.auth.authentication_manager import AuthenticationManager

        exp = int((datetime.now() + timedelta(hours=1)).timestamp())
        token = jwt.encode({"exp": exp}, "", algorithm="none")
        mock_post.return_value = _make_ok_response({"token": token})

        am = AuthenticationManager(platform="cpd", verify_ssl=False)
        am._fetch_cpd_token()

        _, kwargs = mock_post.call_args
        assert kwargs.get("verify") is False

    @patch("common.auth.authentication_manager.requests.post")
    @patch("common.core.base_adapter.requests.request")
    def test_adapter_execute_get_uses_verify_true(self, mock_request, mock_post):
        """BaseMDMAdapter.execute_get must pass verify=True to requests.request."""
        from common.core.base_adapter import BaseMDMAdapter
        from common.auth.authentication_manager import (
            AuthenticationManager,
            invalidate_shared_auth_manager,
        )

        invalidate_shared_auth_manager()

        mock_response = _make_ok_response({"result": "ok"})
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        auth = AuthenticationManager(platform="local", verify_ssl=True)
        adapter = BaseMDMAdapter(
            api_base_url="https://mdm.example.com",
            verify_ssl=True,
            auth_manager=auth,
        )

        adapter.execute_get("/test/endpoint")

        _, kwargs = mock_request.call_args
        assert kwargs.get("verify") is True

    @patch("common.auth.authentication_manager.requests.post")
    @patch("common.core.base_adapter.requests.request")
    def test_adapter_execute_post_uses_verify_true(self, mock_request, mock_post):
        """BaseMDMAdapter.execute_post must pass verify=True to requests.request."""
        from common.core.base_adapter import BaseMDMAdapter
        from common.auth.authentication_manager import (
            AuthenticationManager,
            invalidate_shared_auth_manager,
        )

        invalidate_shared_auth_manager()

        mock_response = _make_ok_response({"result": "created"})
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        auth = AuthenticationManager(platform="local", verify_ssl=True)
        adapter = BaseMDMAdapter(
            api_base_url="https://mdm.example.com",
            verify_ssl=True,
            auth_manager=auth,
        )

        adapter.execute_post("/test/endpoint", json_data={"key": "value"})

        _, kwargs = mock_request.call_args
        assert kwargs.get("verify") is True
