from bs4 import BeautifulSoup
import json
import sys

try:
    with open("vaquero-discounts.html", "r") as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # 1. Check title
    if "Vaquero Discounts" not in soup.title.string:
        print("FAIL: Title incorrect")
        sys.exit(1)

    # 2. Check JSON data
    script_content = ""
    for script in soup.find_all('script'):
        if "const DISCOUNTS =" in script.text:
            script_content = script.text
            break

    if not script_content:
        print("FAIL: JSON script block not found")
        sys.exit(1)

    # Extract JSON part (very naive extraction for testing)
    start_marker = "const DISCOUNTS ="
    start_index = script_content.find(start_marker) + len(start_marker)
    # The JSON ends before the next variable declaration or block end.
    # In my template it is followed by "\n\n        // --- CONFIG ---"
    # But let's just try to grab until the first semicolon?
    # Actually the script has ? No, my template didn't add semicolon explicitly in f-string maybe?
    # Let's check the python script:  - yes it has semicolon if I added it?
    # Wait, looking at :  -> it has a semicolon.

    end_index = script_content.find(";", start_index)
    json_str = script_content[start_index:end_index].strip()

    data = json.loads(json_str)
    if len(data) < 10:
        print(f"FAIL: Not enough data points found ({len(data)})")
        sys.exit(1)

    # 3. Check for critical UI elements
    ids = ['searchInput', 'categoryContainer', 'eligibilityContainer', 'featuredSection', 'resultsGrid']
    for i in ids:
        if not soup.find(id=i):
            print(f"FAIL: Element #{i} not found")
            sys.exit(1)

    print("SUCCESS: HTML structure and Data verification passed.")

except Exception as e:
    print(f"FAIL: Exception during test: {e}")
    sys.exit(1)
