import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

def within_last_five_years(date_str):
    try:
        event_date = datetime.strptime(date_str, "%b %d, %Y")
        return (datetime.now() - event_date).days <= 1825
    except ValueError:
        return False

async def scrape_documents(url, filename):
    base_url = "https://investor.nvidia.com/events-and-presentations/events-and-presentations/default.aspx"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)

        data_collection = []
        while True:
            # Debug: Checking number of articles on the current page
            articles = await page.query_selector_all("div.index-item")
            print(f"Found {len(articles)} articles on the page.")

            for article in articles:
                # Extracting the article date
                date_element = await article.query_selector(".index-item-text-info-date")
                if date_element:
                    date_text = await date_element.text_content()
                    if not within_last_five_years(date_text):
                        print("Reached documents older than 5 years.")
                        await browser.close()
                        return

                # Extracting the article title and link
                title_element = await article.query_selector("h3.index-item-text-title a")
                if title_element:
                    event_name = await title_element.text_content()
                    detail_page_url = await title_element.get_attribute('href')
                    print(f"Visiting detail page for: {event_name}")

                    # Visit the detail page
                    await page.goto(detail_page_url)

                    # Check if there is a PDF link on the detail page
                    pdf_link_element = await page.query_selector("a[type='application/pdf']")
                    if pdf_link_element:
                        href = await pdf_link_element.get_attribute('href')
                        absolute_url = href if href.startswith("http") else f"{base_url}{href}"

                        # Create the data structure
                        data_entry = {
                            "equity_ticker": "NVDA",
                            "source_type": "company_information",
                            "event_type": "press release",
                            "event_name": event_name.strip(),
                            "event_date": date_text.strip(),
                            "data": [{
                                "file_name": absolute_url.split('/')[-1],
                                "file_type": absolute_url.split('.')[-1] if '.' in absolute_url else 'link',
                                "date": date_text.strip(),
                                "category": event_name.strip(),
                                "source_url": absolute_url,
                                "wissen_url": "NULL"
                            }]
                        }
                        data_collection.append(data_entry)

                    await page.go_back()  # Go back to the main page

            # Check for the "Next" page button
            next_button = await page.query_selector("li.next a")
            if next_button:
                next_page_url = await next_button.get_attribute('href')
                if next_page_url:
                    # Correctly combine base URL with the next page link
                    if next_page_url.startswith("/"):
                        next_page_url = f"{base_url}{next_page_url}"
                    elif next_page_url.startswith("?"):
                        next_page_url = f"{base_url}{next_page_url}"
                    print(f"Navigating to the next page: {next_page_url}")
                    await page.goto(next_page_url)
                else:
                    print("No more pages to navigate.")
                    break
            else:
                print("No next button found or pagination ended.")
                break

        await browser.close()

        # Output for debugging or saving to file
        for data in data_collection:
            print(data)  # Adjust according to your data handling needs

async def main():
    url = 'https://nvidianews.nvidia.com/news'
    filename = 'NVDA_PressReleases.json'
    await scrape_documents(url, filename)

if __name__ == "__main__":
    asyncio.run(main())