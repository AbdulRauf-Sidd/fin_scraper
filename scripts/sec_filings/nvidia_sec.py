import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

EQUITY_TICKER = "NVDA"
YEARS_TO_SCRAPE = 5
JSON_FILENAME = "JSON/Nvidia.json"
NVIDIA_SEC_FILINGS_URL = "https://investor.nvidia.com/financial-info/sec-filings/default.aspx"

# Ensure the JSON directory exists
os.makedirs(os.path.dirname(JSON_FILENAME), exist_ok=True)

# Calculate the last N years to scrape
CURRENT_YEAR = datetime.now().year
YEARS_LIST = list(range(CURRENT_YEAR, CURRENT_YEAR - YEARS_TO_SCRAPE, -1))  # e.g., [2025, 2024, 2023, 2022, 2021]


async def enable_stealth(page):
    """Inject JavaScript to evade bot detection."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)


async def parse_date(date_str):
    """Parse date in format: Dec 18, 2024."""
    date_str = date_str.strip()
    formats = ["%b %d, %Y"]  # Example: Dec 18, 2024

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    print(f"⚠️ Error parsing date: {date_str}")
    return None


async def select_year(page, year):
    """Select a specific year from the dropdown and wait for the page to update."""
    try:
        dropdown = await page.wait_for_selector("select")
        await dropdown.select_option(str(year))

        # Wait for the filings list to update
        await asyncio.sleep(5)  # Allow time for content to load
        print(f"✅ Selected Year: {year}")
    except Exception as e:
        print(f"⚠️ Error selecting year {year}: {e}")


async def extract_files_from_page(page, year):
    """Extracts filing dates, filing type, descriptions, and file links from SEC filings (div.module_item)."""
    try:
        await page.wait_for_selector("div.module_item", timeout=10000)

        filing_rows = await page.query_selector_all("div.module_item")  # Extract all filing rows
        if not filing_rows:
            print(f"⚠️ No filings found for year {year}.")
            return []

        filings = []
        for row in filing_rows:
            try:
                # Extract Filing Date
                date_element = await row.query_selector("div.filing-date, div.date, span")  # Different possible elements for date
                filing_date = await date_element.inner_text() if date_element else ""

                # Ensure we only process valid filing dates
                filing_date_parsed = await parse_date(filing_date)
                if not filing_date_parsed:
                    continue  # Skip this row if date is invalid

                # Extract Filing Type
                filing_type_element = await row.query_selector("div.filing-type, div.form, a")
                filing_type = await filing_type_element.inner_text() if filing_type_element else "Unknown Form"

                # Extract Filing Description
                description_element = await row.query_selector("div.filing-desc, div.description, p")
                description = await description_element.inner_text() if description_element else "No Description"

                # Extract Download/View Links (PDF, Excel)
                file_links = []
                link_elements = await row.query_selector_all("a[href]")

                for link in link_elements:
                    file_url = await link.get_attribute("href")
                    file_name = file_url.split("/")[-1] if file_url else "unknown"

                    # Determine file type (PDF, XLS)
                    if ".pdf" in file_url.lower():
                        file_type = "pdf"
                    elif ".xls" in file_url.lower() or ".xlsx" in file_url.lower():
                        file_type = "excel"
                    else:
                        file_type = "unknown"

                    # Ensure absolute URL
                    full_url = file_url if file_url.startswith("http") else f"https://investor.nvidia.com{file_url}"

                    file_links.append({
                        "file_name": file_name,
                        "file_type": file_type,
                        "date": filing_date_parsed.strftime("%Y/%m/%d"),
                        "category": "report",
                        "source_url": full_url,
                        "wissen_url": "unknown"
                    })

                # Store extracted data
                if file_links:
                    filings.append({
                        "equity_ticker": EQUITY_TICKER,
                        "source_type": "company_information",
                        "event_name": description,
                        "event_date": filing_date_parsed.strftime("%Y/%m/%d"),
                        "filing_type": filing_type,
                        "data": file_links
                    })
                    print(f"📄 Extracted filing: {filing_date} - {filing_type} ({len(file_links)} files)")

            except Exception as e:
                print(f"⚠️ Error processing row: {e}")

        return filings
    except Exception as e:
        print(f"⚠️ Error extracting files for year {year}: {e}")
        return []


async def scrape_nvidia_sec_filings():
    """Main function to scrape NVIDIA SEC filings for multiple years."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Run in visible mode
        context = await browser.new_context()
        page = await context.new_page()
        await enable_stealth(page)

        print(f"🔍 Navigating to {NVIDIA_SEC_FILINGS_URL}")
        try:
            await page.goto(NVIDIA_SEC_FILINGS_URL, wait_until="load", timeout=120000)

            all_filings = []
            for year in YEARS_LIST:
                await asyncio.sleep(5)  # Artificial delay to mimic human behavior
                await select_year(page, year)  # Select the desired year
                await asyncio.sleep(5)  # Another delay after selection

                filings_data = await extract_files_from_page(page, year)
                if filings_data:
                    all_filings.extend(filings_data)

            if all_filings:
                with open(JSON_FILENAME, "w", encoding="utf-8") as f:
                    json.dump(all_filings, f, indent=4)
                print(f"\n✅ SEC filings for the last {YEARS_TO_SCRAPE} years saved in: {JSON_FILENAME}")
            else:
                print("\n❌ No filings found for the selected years.")

        except Exception as e:
            print(f"⚠️ Error loading page: {e}")

        await browser.close()


# Run the scraper
asyncio.run(scrape_nvidia_sec_filings())
