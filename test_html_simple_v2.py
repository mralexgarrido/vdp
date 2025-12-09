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
    start_marker = "const DISCOUNTS ="
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("FAIL: JSON script block not found")
        sys.exit(1)

    start_idx += len(start_marker)
    # Search for the semicolon that terminates the assignment
    # We assume the array closing bracket is before that.
    # But wait, my build script logic was:
    # const DISCOUNTS = {discounts_json};
    # So searching for semicolon is actually correct.

    # We must skip whitespace
    while content[start_idx].isspace():
        start_idx += 1

    # Now we are at '['
    if content[start_idx] != '[':
        print("FAIL: JSON did not start with [")
        sys.exit(1)

    # Find the next semicolon
    end_idx = content.find(";", start_idx)
    if end_idx == -1:
         print("FAIL: Semicolon not found")
         sys.exit(1)

    json_str = content[start_idx:end_idx]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"FAIL: JSON decode error: {e}")
        # Debug print a tail of the json string
        print(f"Tail of JSON string: {json_str[-50:]}")
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
