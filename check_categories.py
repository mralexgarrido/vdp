import urllib.request
import csv
import io

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQregHbek9Lten27U-Hs92yB81IoGO3PyJGOOekrIkTeXpI9XRV-YMaw-DNTZk-MCQTEhLcqkB3kMF5/pub?output=csv"
response = urllib.request.urlopen(url)
csv_data = response.read().decode('utf-8')
f = io.StringIO(csv_data)
reader = csv.DictReader(f)

categories = set()
for row in reader:
    cat = row.get("Category", "").strip()
    if cat:
        categories.add(cat)
    else:
        categories.add("Other")

print("Unique Categories:")
for c in sorted(list(categories)):
    print(f"- {c}")
