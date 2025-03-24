from playwright.sync_api import sync_playwright
import csv
import time
import os

url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000021344&type=&dateb=&owner=include&count=100&search_text="

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set True for headless mode
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded")

    data = []
    page_number = 1  # Track pagination progress

    while True:  # Loop through all pages
        time.sleep(3)  # Short delay for safety

        # **Check if page is invalid**
        if "Invalid parameter" in page.title():
            print("❌ Reached 'Invalid parameter' page. Stopping.")
            break

        try:
            page.wait_for_selector("table.tableFile2", timeout=10000)  # Wait for table
        except:
            print("⚠️ Table not found! Check if the website structure changed.")
            break

        rows = page.locator("table.tableFile2 tr").all()
        print(f"📄 Page {page_number}: Total rows found: {len(rows)}")

        for row in rows[1:]:  # Skip header row
            columns = row.locator("td").all()

            if len(columns) >= 5:
                document_type = columns[0].inner_text().strip()

                try:
                    document_link_element = columns[1].locator("a")
                    document_link = document_link_element.get_attribute("href") if document_link_element.count() > 0 else ""
                    document_link = f"https://www.sec.gov{document_link}" if document_link else "N/A"
                except:
                    document_link = "N/A"

                # Filter document links to only include those ending with .htm
                if not document_link.endswith(".htm"):
                    continue

                description = columns[2].inner_text().strip()
                # Remove content after <br> in the description
                description = description.split("<br>")[0].strip()

                date = columns[3].inner_text().strip()

                data.append([document_type, document_link, description, date])

        # **Find the "Next 100" button**
        next_buttons = page.locator("input[value='Next 100']")
        if next_buttons.count() > 0:
            next_buttons.first.click()  # Click the first "Next 100" button
            page.wait_for_load_state("domcontentloaded")  # Ensure new page loads
            time.sleep(3)  # Give time for content to refresh
            page_number += 1  # Increment page counter
        else:
            print("✅ No more pages left to scrape.")
            break  # Exit loop when no "Next 100" button

    browser.close()

    # Save to CSV
    output_directory = os.path.join(os.path.expanduser("~"), "Documents")  # Changed to Documents folder
    output_file_path = os.path.join(output_directory, "sec_data.csv")

    if data:
        try:
            with open(output_file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Document Type", "Document Link", "Description", "Date"])
                writer.writerows(data)
            print(f"✅ Scraping complete. Data saved to {output_file_path}")
        except PermissionError:
            print(f"❌ Permission denied. Could not save file to {output_file_path}.")
        except Exception as e:
            print(f"❌ An error occurred while saving the file: {e}")
    else:
        print("⚠️ No data extracted. Try checking if the website structure has changed.")