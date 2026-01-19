<!--
This file has been modified with the assistance of IBM Bob (AI Code Assistant)
-->

# IBM MDM MCP Server - Sample Queries

Simple, natural language prompts that work with Claude Desktop. The tools handle the complexity automatically.

## ⚠️ IMPORTANT DISCLAIMER

### Purpose of This Document
This document provides **illustrative query patterns** to demonstrate the diverse ways you can interact with IBM MDM through natural language. These examples showcase various use cases and scenarios to help you understand the capabilities and inspire your own queries.

### Data Variability
**These are example patterns only.** Your actual IBM MDM instance will have:
- **Different entity types** (e.g., "customer", "product", "asset" instead of "person", "organization")
- **Different field names** (e.g., "surname" instead of "last_name", "location" instead of "city")
- **Different data structures** based on your specific business domain and configuration

### Response Accuracy
**All responses are based solely on data returned by the underlying IBM MDM APIs.**

When using AI assistants like Claude Desktop, the assistant can only:
- Display data that exists in your MDM system
- Count records returned by API queries
- Format and present information from API responses

The AI assistant **cannot**:
- Generate, estimate, or infer data not present in API responses
- Perform calculations beyond what the API provides
- Create synthetic data or statistics

**Note:** These limitations apply regardless of which MCP-compatible AI client you use (Claude Desktop, or other MCP clients).

### Before Using Examples
1. **Always explore YOUR data model first** by asking: "What entity types and searchable fields are available in my MDM system?"
2. **Replace all placeholders** (`[entity_type]`, `[field_name]`, `[value]`) with your actual field names
3. **Verify field names** match your data model exactly

### Placeholder Legend
- `[entity_type]` - Replace with your actual entity type (customer, product, account, etc.)
- `[field_name]` - Replace with your actual field name (name, status, region, etc.)
- `[value]` - Replace with your actual search value

---

## 📋 Quick Reference

The MCP server tools automatically:
- Fetch the data model when needed
- Validate property paths
- Handle authentication
- Format responses

Just ask naturally!

---

## ⚠️ Important: Tips for Best Results

### ✅ Good Prompts
- "Find customers with last name Smith in Boston"
- "Show me person records with missing email addresses"
- "Count how many records I have in each city"
- "Get complete details for record ID 12345"

### ❌ Avoid
- Vague requests without specific criteria
- Asking for "all records" without limits
- Requesting data aggregations or calculations not in the raw data
- Assuming field names without checking

### 🎯 For Accurate Reports & Analytics

**CRITICAL:** Claude can only report what the MDM API returns. To prevent hallucination:

✅ **DO:**
- Ask for counts from separate queries: "Count records in Boston, then count records in New York, then compare"
- Request raw data first: "Show me the first 20 customer records"
- Use explicit limits: "Find 10 person records with last name Smith"
- Ask for one metric at a time: "How many person records are there?"

❌ **DON'T:**
- Ask for calculations not in the data: "Calculate average age" (unless age is a field)
- Request aggregations in one query: "Group all records by city and count them"
- Expect statistical analysis: "Show me the distribution curve"
- Ask for derived metrics: "Calculate customer lifetime value"

**For Reports:** Add this to your prompt:
> "Only use actual data from the API responses. Do not calculate, estimate, or infer any values. If you need to count or compare, run separate queries for each category."

---

## 📊 Quick Report Templates

These templates help you generate visual dashboards and reports. All use only actual API data.

**Template 1: Distribution Dashboard**
```
Create a visual distribution dashboard for [entity_type] by [field_name]:
1. Count records where [field_name] equals [value1] (run search, show API count)
2. Count records where [field_name] equals [value2] (run search, show API count)
3. Count records where [field_name] equals [value3] (run search, show API count)
4. Display results as:
   - A formatted table: [Field] | Record Count
   - A simple bar chart visualization using ASCII or text
   - Highlight the category with the most records
5. IMPORTANT: Only use exact counts from API responses
6. Do not calculate percentages, averages, or totals unless explicitly requested
```

**Template 2: Data Quality Dashboard**
```
Generate a data quality dashboard for [entity_type]:
1. Count total [entity_type] records (show API count)
2. Count records with potential duplicates (show API count)
3. Count records with missing [field1] (show API count)
4. Count records with missing [field2] (show API count)
5. Display as:
   - Summary table: Issue Type | Count
   - Visual indicator showing data quality score
   - Highlight top issues needing attention
6. Use only actual API response numbers
```

**Template 3: Entity Type Overview Dashboard**
```
Create an entity type overview dashboard:
1. First, get my data model to see available entity types
2. For each entity type found, count records (show API result)
3. Display as:
   - Table: Entity Type | Count | Percentage of Total
   - Visual breakdown (pie chart representation)
   - Summary statistics
4. Only report actual numbers from API
5. Calculate percentages only from the actual counts returned
```

**Template 4: Trend Comparison Chart**
```
Create a comparison chart for [entity_type] across [field_name]:
1. Count records for each value of [field_name]
2. Display as:
   - Comparison table with counts
   - Side-by-side bar chart visualization
   - Ranking from highest to lowest
   - Identify top 3 and bottom 3
3. Use only API-returned data
```

---

## 🔄 Common Usage Patterns

### Pattern 1: Explore → Search → Details
```
1. "What searchable fields are available for customer records?"
2. "Find customer records where status equals active and region equals northeast"
3. "Get complete details for record ID 12345"
```

### Pattern 2: Quality Check → Review → Fix
```
1. "Find all records with potential duplicates"
2. "Show me the details for the first duplicate record"
3. "Get all entities for that record to see the source data"
```

### Pattern 3: Regional Distribution Dashboard
```
"Create a regional distribution dashboard for customer records:
1. Count records in north region (show API count)
2. Count records in south region (show API count)
3. Count records in east region (show API count)
4. Count records in west region (show API count)
5. Display as:
   - Table: Region | Count
   - Simple bar chart showing relative sizes
   - Identify which region has the most customers
6. Only use actual API counts, no estimates"
```

### Pattern 4: Data Quality Report Generation
```
"Generate a data quality dashboard for customer records:
1. Count total customer records (show API count)
2. Count records with potential duplicates (show API count)
3. Count records with missing email addresses (show API count)
4. Count records with missing phone numbers (show API count)
5. Display as:
   - Summary table: Issue Type | Count
   - Visual indicator showing data quality score
   - Highlight top issues needing attention
6. Use only actual API response numbers"
```

### Pattern 5: Entity Type Overview
```
"Create an entity type overview dashboard:
1. First, get my data model to see available entity types
2. For each entity type found, count records (show API result)
3. Display as:
   - Table: Entity Type | Count | Percentage of Total
   - Visual breakdown using text-based pie chart
   - Summary statistics
4. Only report actual numbers from API
5. Calculate percentages only from the actual counts returned"
```

---

## Data Model Exploration

### Understanding Your Data
```
What entity types and searchable fields are available in my MDM system?
```

### Exploring Specific Entities
```
Show me all searchable attributes for person records
```

```
What fields can I search on for organization entities?
```

---

## Basic Searches

### Simple Searches
```
Find all records with last name "Smith"
```

```
Search for customers in Boston
```

```
Find person records with email containing "@ibm.com"
```

```
Show me organizations in New York
```

### Multiple Conditions (AND)
```
Find customers with last name "Smith" in Boston
```

```
Search for person records where first name is "John" and city is "Chicago"
```

```
Find organizations in California with revenue over 1000000
```

### Alternative Conditions (OR)
```
Find records where last name is "Smith" or "Jones"
```

```
Search for customers in Boston or New York
```

```
Find person records with last name "Smith", "Jones", or "Brown"
```

---

## Advanced Searches

### Complex Nested Logic
```
Find people named Smith or Jones who live in Boston
```

```
Search for (customers in Boston or New York) with last name "Smith"
```

```
Find records where (last name is "Smith" and city is "Boston") or (last name is "Jones" and city is "New York")
```

### Pattern Matching
```
Find all records where email contains "gmail"
```

```
Search for customers whose last name starts with "Mc"
```

```
Find records where phone number starts with "+1-617"
```

```
Search for fuzzy matches of the name "Smyth"
```

### Range Queries
```
Find person records where age is between 25 and 40
```

```
Search for organizations with revenue greater than 500000
```

```
Find records created in the last 30 days
```

---

## Data Quality

### Finding Issues
```
Find all records with potential duplicates
```

```
Show me person records with data quality issues
```

```
Search for potential duplicate customers with last name "Smith"
```

```
Find records with potential matches that need review
```

### Missing Data
```
Find all person records that are missing email addresses
```

```
Search for customers with no phone number
```

```
Show me records where the address field is empty
```

---

## Analytical Queries

### Counting Records
```
How many person records do I have in total?
```

```
Count all customer records in Boston
```

```
How many records have potential duplicates?
```

### Distribution Analysis
```
Show me the count of records for each entity type (person, organization, etc.)
```

```
Count how many customer records I have in Boston, New York, and Chicago
```

```
How many records do I have from each source system?
```

### Comparisons
```
Compare the number of person records in Boston vs New York
```

```
Show me which city has the most customer records
```


---

## Record Details

### Getting Specific Records
```
Get the complete details for record ID 12345
```

```
Show me all information for record xyz789
```

### Related Entities
```
Show me all entities associated with record ID 12345
```

```
Get all source system records that contribute to record 67890
```

```
What entities are linked to record abc123?
```

---

## Business Scenarios

**Note:** Replace placeholders with your actual entity types, field names, and values from your data model.

### High-Value Records
```
Find [entity_type] where [value_field] is greater than [threshold] and [location_field] is in [location_list]
```

**Example:**
```
Find customers where annual_revenue is greater than 1000000 and region is in ["north", "west"]
```

### Data Quality Audits
```
Find all [entity_type] records where [date_field] is older than [date]
```

```
Show me [entity_type] records with missing [field1] or [field2]
```

```
Search for records with data quality issues where [field_name] equals "[value]"
```

### Compliance & Verification
```
Find all records that need review for compliance
```

```
Search for [entity_type] with incomplete [field_name] information
```

```
Show me records from multiple source systems that may need reconciliation
```

### Source System Queries
```
Find all records from the [source_system_name] system
```

```
Search for [entity_type] that exist in both [source1] and [source2] systems
```

```
Show me records from [source_system] that need migration
```

---

## Filtering & Refinement

### Entity Type Filters
```
Find all [entity_type] records where [field_name] equals "[value]"
```

**Example:**
```
Find all customer records where status equals "active"
```

### Source Filters
```
Find records from the [source_system] system where [field_name] equals "[value]"
```

**Example:**
```
Find records from the CRM system where account_type equals "enterprise"
```

### Relationship Filters
```
Find all [relationship_type] relationships
```

**Example:**
```
Find all customer-account relationships
```

---

## Pagination & Large Datasets

### Controlled Results
```
Show me the first 50 customer records
```

```
Find person records with last name "Smith", limit to 20 results
```

### Browsing Results
```
Get the next page of search results (offset 20, limit 20)
```

```
Show me records 100-150 from my previous search
```

---

## 💡 Pro Tips for Accurate Results

- Start with small result sets (10-20 records)
- Use specific search criteria
- For counts/distributions, ask for each category separately
- Add "only use actual API data" to prevent hallucination
- Check the data model first if unsure about field names
- When generating reports, explicitly state "use only API response numbers"

---

## Need Help?

- The tools automatically handle data model fetching
- Property paths are validated automatically
- Authentication is managed for you
- Results are formatted clearly

Just ask naturally and let the tools do the work!

---

**Version:** 1.0.0  
**Last Updated:** January 2026