import csv
import json
import urllib.request
import io

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQregHbek9Lten27U-Hs92yB81IoGO3PyJGOOekrIkTeXpI9XRV-YMaw-DNTZk-MCQTEhLcqkB3kMF5/pub?output=csv"
OUTPUT_CSV = "categorized_discounts.csv"

def parse_who_can_redeem(text):
    """Parses the 'Who Can Redeem' text into a list."""
    roles = []
    text_lower = text.lower()
    if "student" in text_lower: roles.append("Students")
    if "faculty" in text_lower: roles.append("Faculty")
    if "staff" in text_lower: roles.append("Staff")
    if "alumni" in text_lower: roles.append("Alumni")

    if not roles:
        return ["Students", "Faculty", "Staff"] # Default fallback
    return roles

def main():
    print(f"Downloading data from {GOOGLE_SHEET_URL}...")
    try:
        response = urllib.request.urlopen(GOOGLE_SHEET_URL)
        csv_data = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    # Parse CSV
    print("Processing data...")
    f = io.StringIO(csv_data)
    reader = csv.DictReader(f)

    processed_rows = []
    row_id = 100 # Start IDs from 100

    # Headers: 'Name of the Business', 'Discount Amount', 'Who Can Redeem', 'How to Redeem', 'About this Business', 'Address', 'Phone', 'Email address', 'Website/Social Media', 'Category', 'VDP Join Date', 'Authorized by', 'Contact Title/Role'

    for row in reader:
        # Extract fields safely
        name = row.get("Name of the Business", "").strip()
        if not name: continue # Skip empty rows

        discount = row.get("Discount Amount", "")
        who_raw = row.get("Who Can Redeem", "")
        how = row.get("How to Redeem", "")
        about = row.get("About this Business", "")
        address = row.get("Address", "")
        phone = row.get("Phone", "")
        email = row.get("Email address", "")
        website = row.get("Website/Social Media", "")

        # New Fields
        category = row.get("Category", "").strip()
        if not category:
            category = "Other"

        join_date = row.get("VDP Join Date", "")
        authorized_by = row.get("Authorized by", "")
        contact_title = row.get("Contact Title/Role", "")

        # Process specific fields
        who_list = parse_who_can_redeem(who_raw)

        # Proximity logic (simple guess)
        proximity = "RGV Area"
        if "," in address:
            parts = address.split(",")
            # usually "Street, City, Zip"
            if len(parts) >= 2:
                proximity = "Near " + parts[-2].strip() # City

        # Feature flag logic
        is_featured = False
        if "free" in discount.lower() or "25%" in discount or "20%" in discount:
             is_featured = True

        # Construct new row
        new_row = {
            "id": str(row_id),
            "businessName": name,
            "category": category,
            "discountAmount": discount,
            "whoCanRedeem": ";".join(who_list), # Join with ; for CSV storage
            "howToRedeem": how,
            "description": about,
            "address": address,
            "phone": phone,
            "email": email,
            "website": website,
            "campusProximity": proximity,
            "isFeatured": str(is_featured),
            "tags": category.split(" ")[0].lower(), # First word of category as tag

            # New Internal Fields
            "joinDate": join_date,
            "authorizedBy": authorized_by,
            "contactTitle": contact_title
        }

        processed_rows.append(new_row)
        row_id += 1

    # Write to Output CSV
    print(f"Writing {len(processed_rows)} entries to {OUTPUT_CSV}...")
    fieldnames = [
        "id", "businessName", "category", "discountAmount", "whoCanRedeem",
        "howToRedeem", "description", "address", "phone", "email",
        "website", "campusProximity", "isFeatured", "tags",
        "joinDate", "authorizedBy", "contactTitle"
    ]

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in processed_rows:
            writer.writerow(row)

    print("Done!")

if __name__ == "__main__":
    main()
