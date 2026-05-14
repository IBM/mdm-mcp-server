# Copyright [2026] [IBM]
# Licensed under the Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
# See the LICENSE file in the project root for license information.

"""
Per-request user token context for identity propagation.

Stores the caller's IBM IAM bearer token in an asyncio ContextVar so that
BaseMDMAdapter can use it instead of the shared service-account token.
The value is set by UserTokenMiddleware at the start of each tool call and
reset (not cleared) when the call completes, preserving any outer value.
"""

from contextvars import ContextVar, Token
from typing import Optional

_user_token: ContextVar[Optional[str]] = ContextVar("_user_token", default=None)


def set_user_token(token: str) -> Token:
    """Store token and return the reset token needed to undo the set."""
    return _user_token.set(token)


def reset_user_token(reset_token: Token) -> None:
    """Restore the ContextVar to the value it held before set_user_token was called."""
    _user_token.reset(reset_token)


def get_user_token() -> Optional[str]:
    """Return the per-request user token, or None if running in service-account mode."""
    return _user_token.get()
