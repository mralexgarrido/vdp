import re
import json
import sys

try:
    with open("vaquero-discounts.html", "r") as f:
        content = f.read()

    # 1. Check title
    if "<title>Vaquero Discounts</title>" not in content:
        print("FAIL: Title incorrect")
        sys.exit(1)

    # 2. Check JSON data
    # Look for: const DISCOUNTS = [...];
    match = re.search(r'const DISCOUNTS = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("FAIL: JSON script block not found")
        sys.exit(1)

    json_str = match.group(1)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"FAIL: JSON decode error: {e}")
        sys.exit(1)

    if len(data) < 10:
        print(f"FAIL: Not enough data points found ({len(data)})")
        sys.exit(1)

    # 3. Check for critical UI elements
    ids = ['searchInput', 'categoryContainer', 'eligibilityContainer', 'featuredSection', 'resultsGrid']
    for i in ids:
        if f'id="{i}"' not in content and f"id='{i}'" not in content:
            print(f"FAIL: Element #{i} not found")
            sys.exit(1)

    print("SUCCESS: HTML structure and Data verification passed.")

except Exception as e:
    print(f"FAIL: Exception during test: {e}")
    sys.exit(1)
