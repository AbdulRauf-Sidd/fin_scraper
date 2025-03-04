import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_pdfs(url, start_year, end_year):
    pdf_data = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Debug Mode
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await asyncio.sleep(3)  # Initial Wait

        for year in range(start_year, end_year + 1):
            print(f"📌 Scraping Year: {year}")

            # Select Year
            await page.select_option("#SecYearSelect", str(year))
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)

            page_number = 1
            while True:
                print(f"🔄 Page {page_number}")

                # Get Rows
                rows = await page.query_selector_all("div.module_item.list--reset:not([aria-hidden='true'])")
                if not rows:
                    print(f"⚠️ No Rows, Retrying Page {page_number}...")
                    await asyncio.sleep(3)
                    continue

                for row in rows:
                    date_element = await row.query_selector("span.module-sec_date-text")
                    desc_element = await row.query_selector("span.module-sec_description-text")
                    pdf_elements = await row.query_selector_all("li.module-sec_download-list-item a")

                    event_date = await date_element.inner_text() if date_element else "No Date"
                    description = await desc_element.inner_text() if desc_element else "No Description"

                    # 🔍 Debugging print to check extracted values
                    print(f"✅ Year: {year} | Date: {event_date} | Description: {description}")

                    # ✅ Format JSON correctly
                    event_data = {
                        "equity_ticker": "CRAWCO",
                        "source_type": "company_information",
                        "frequency": "periodic",
                        "event_type": "SEC Filing",
                        "event_name": description.strip(),  # ✅ Ensure event_name is set properly
                        "event_date": event_date.strip(),
                        "data": []
                    }

                    for pdf in pdf_elements:
                        href = await pdf.get_attribute("href")
                        if href and ".pdf" in href:
                            file_name = href.split("/")[-1]  # Extract file name from URL
                            event_data["data"].append({
                                "file_name": file_name,
                                "file_type": ".pdf",
                                "date": event_date.strip(),
                                "category": "report",
                                "source_url": f"https:{href}",
                                "wissen_url": f"https://ourstorage.com/{file_name}"
                            })

                    # ✅ Append event_data instead of separate PDF entries
                    pdf_data.append(event_data)

                # Get pagination buttons
                pagination_buttons = await page.query_selector_all("button.pager_button.pager_page")

                # Find the button for the next page
                next_page_number = page_number + 1
                next_button = None

                for button in pagination_buttons:
                    btn_text = await button.inner_text()
                    if btn_text.isdigit() and int(btn_text) == next_page_number:
                        next_button = button
                        break

                if next_button:
                    # Click the next page button
                    await next_button.click()
                    await asyncio.sleep(3)  # Allow page update

                    # Verify the page number update
                    active_page = await page.query_selector("button.pager_button.pager_page[aria-current='true']")
                    current_page = await active_page.inner_text() if active_page else None

                    if current_page and int(current_page) == next_page_number:
                        page_number += 1
                        continue
                    else:
                        print(f"⚠️ Error: Page did not advance to {next_page_number}, stopping.")
                        break
                else:
                    print(f"✅ Finished Year {year}")
                    break

        await browser.close()

    if pdf_data:
        print(f"✅ Total events found: {len(pdf_data)}")
        with open("sec_filings.json", "x") as f:
            json.dump(pdf_data, f, indent=4)
            print("\n🎯 Data saved to `sec_filings.json`")
    else:
        print("❌ No PDFs found.")

if __name__ == "__main__":
    url = "https://ir.crawco.com/financials/default.aspx"
    asyncio.run(scrape_pdfs(url, 2019, 2025))