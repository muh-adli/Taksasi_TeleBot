import os
from bs4 import BeautifulSoup
import pandas as pd

# Define input and output directories
input_dir = "html"
output_dir = "result"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get all HTML files in the input directory
html_files = [f for f in os.listdir(input_dir) if f.endswith(".html")]

# Process each HTML file
for html_file in html_files:
    html_path = os.path.join(input_dir, html_file)
    html_name = os.path.splitext(html_file)[0]  # Remove .html extension
    output_file = os.path.join(output_dir, f"{html_name}.xlsx")

    # Read the HTML file
    with open(html_path, "r", encoding="utf-8") as file:
        html = file.read()

    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Extract all elements with class "field-name"
    data = []
    for li in soup.find_all("li", class_="upload-item"):
        field_name_elem = li.find("span", class_="field-name")
        field_group_elem = li.find("span", class_="field-group")
        field_area_elem = li.find("span", class_="field-area")

        # Extract values, ensuring we don't add None
        field_name = field_name_elem.get_text(strip=True) if field_name_elem else "N/A"
        field_group = field_group_elem.get_text(strip=True) if field_group_elem else "N/A"
        field_area = field_area_elem.get_text(strip=True) if field_area_elem else "N/A"

        data.append([field_name, field_group, field_area])

    # Ensure all data is captured
    print(f"File: {html_file} → Extracted {len(data)} records")

    # Create a DataFrame and save to Excel
    df = pd.DataFrame(data, columns=["Field Name", "Field Group", "Field Area"])
    df.to_excel(output_file, index=False)

print("All files processed successfully!")
