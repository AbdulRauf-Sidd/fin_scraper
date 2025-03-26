import asyncio
from playwright.async_api import async_playwright
import csv
import os


async def extract_row_data(row):
    """Extracts data from a single row asynchronously."""
    try:
        columns = await row.locator("td").all()
        if len(columns) < 5:
            return None  # Skip if row is incomplete

        document_type = await columns[0].inner_text()

        # ✅ Process multiple row elements asynchronously
        document_link_element = columns[1].locator("a#documentsbutton")
        document_link = await document_link_element.get_attribute("href") if await document_link_element.count() > 0 else "N/A"
        document_link = f"https://www.sec.gov{document_link}" if document_link and document_link != "N/A" else "N/A"

        # Filter document links to only include those ending with .htm
        if not document_link.endswith(".htm"):
            return None  # Skip unwanted links

        description_task = columns[2].inner_text()
        date_task = columns[3].inner_text()

        description, date = await asyncio.gather(description_task, date_task)

        return [document_type.strip(), document_link, description.strip(), date.strip()]
    except Exception as e:
        print(f"❌ Error extracting row data: {e}")
        return None


async def scrape_page(url: str, page_number: int, context):
    """Scrapes a single page and returns data."""
    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded")
    data = []

    await asyncio.sleep(2)  # Short delay for stability

    if "Invalid parameter" in await page.title():
        print(f"❌ Page {page_number}: Reached 'Invalid parameter' page. Skipping.")
        await page.close()
        return []

    try:
        await page.wait_for_selector("table.tableFile2", timeout=10000)  # Ensure table is present
    except:
        print(f"⚠️ Page {page_number}: Table not found! Possible website structure change.")
        await page.close()
        return []

    rows = await page.locator("table.tableFile2 tr").all()
    print(f"📄 Page {page_number}: Processing {len(rows) - 1} rows...")

    # **Run all row extractions concurrently**
    row_tasks = [extract_row_data(row) for row in rows[1:]]  # Skip header row
    results = await asyncio.gather(*row_tasks)

    # Filter out None values
    data.extend(filter(None, results))

    await page.close()
    return data


async def scrape_sec_data_concurrently(base_url: str, output_file_path: str, max_workers: int = 5):
    """Scrapes multiple pages in parallel using asyncio."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await context.new_page()
        await page.goto(base_url, wait_until="domcontentloaded")

        # **Get all page links to scrape**
        page_urls = [base_url]
        page_number = 1

        while True:
            next_buttons = page.locator("input[value='Next 100']")
            if await next_buttons.count() > 0:
                await next_buttons.first.click()
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(2)  # Ensure page loads
                page_number += 1
                page_urls.append(page.url)
            else:
                print("✅ No more pages found.")
                break  # Stop if no more pages

        await page.close()

        # **Process multiple pages in parallel**
        print(f"🔄 Scraping {len(page_urls)} pages in parallel with {max_workers} workers...")
        semaphore = asyncio.Semaphore(max_workers)  # Limit concurrency to avoid memory issues

        async def worker(url, page_num):
            async with semaphore:
                return await scrape_page(url, page_num, context)

        page_tasks = [worker(url, i + 1) for i, url in enumerate(page_urls)]
        all_data = await asyncio.gather(*page_tasks)

        await browser.close()

        # Flatten the results
        data = [item for sublist in all_data for item in sublist]

        # Ensure the output directory exists
        output_directory = os.path.join(os.path.expanduser("~"), "Documents")
        os.makedirs(output_directory, exist_ok=True)
        output_file_path = os.path.join(output_directory, output_file_path)

        # Debugging: Print first few extracted rows
        if data:
            print("🔹 First 5 extracted rows:")
            for row in data[:5]:
                print(row)

        # Save to CSV
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
            print("⚠️ No data extracted. Check if the website structure changed.")


# **Run the function asynchronously**
if __name__ == "__main__":
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000021344&type=&dateb=&owner=include&count=100&search_text="
    output_file = "sec_data.csv"
    max_parallel_pages = 5  # Adjust based on system resources

    asyncio.run(scrape_sec_data_concurrently(url, output_file, max_parallel_pages))
