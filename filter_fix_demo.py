#!/usr/bin/env python3
"""
Demo script showing the correct filter format after the fix.

BEFORE (caused error):
{
  "limit": 15,
  "query": "ambulance fraud Medicare Medicaid emergency medical transportation",
  "filters": {
    "data_source": {
      "eq": "GAO"
    }
  }
}

AFTER (correct format):
{
  "limit": 15,
  "query": "ambulance fraud Medicare Medicaid emergency medical transportation",
  "filter": "data_source eq 'GAO'"
}
"""

import json

# The problematic query that was causing the error
old_format = {
    "limit": 15,
    "query": "ambulance fraud Medicare Medicaid emergency medical transportation",
    "filters": {"data_source": {"eq": "GAO"}},
}

# The correct format after our fix
new_format = {
    "limit": 15,
    "query": "ambulance fraud Medicare Medicaid emergency medical transportation",
    "filter": "data_source eq 'GAO'",
}

print("❌ OLD FORMAT (caused Filter validation failed error):")
print(json.dumps(old_format, indent=2))
print("\n✅ NEW FORMAT (correct OData syntax):")
print(json.dumps(new_format, indent=2))
print("\n🔧 What changed:")
print("1. Parameter name: 'filters' → 'filter'")
print("2. Format: object with nested structure → OData string")
print('3. Value: {"data_source": {"eq": "GAO"}} → "data_source eq \'GAO\'"')
