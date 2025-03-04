import asyncio
import random
import json
import argparse
import traceback
from datetime import datetime
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import re
from utils import * 

# Argument Parsing
parser = argparse.ArgumentParser(description="SEC Filings Scraper")
parser.add_argument("url", type=str, help="SEC Filings page URL")
parser.add_argument("ticker", type=str, help="Equity ticker symbol")
parser.add_argument("--output", type=str, default="sec_filings.json", help="Output JSON file name")

args = parser.parse_args()

# Configurations
SEC_FILINGS_URL = args.url
EQUITY_TICKER = args.ticker.upper()  # Convert to uppercase for standardization
JSON_FILENAME = args.output
VALID_YEARS = {str(year) for year in range(2019, 2026)}  # 2019-2025

# Track visited pages
visited_urls = set()
file_links_collected = []
stop_scraping = False



async def enable_stealth(page):
    """Inject JavaScript to evade bot detection."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)


from dateutil.parser import parse

import asyncio




async def parse_date3(date_str):
    """Parses a date string like 'Tuesday, February 25, 2025' into 'YYYY/MM/DD' format."""
    try:
        parsed_date = parse(date_str, fuzzy=True)
        return parsed_date  # Returns a datetime object
    except Exception as e:
        print(f"⚠️ Error parsing date: {date_str} -> {e}")
        return None  # Return None if parsing fails


import re
from urllib.parse import urljoin
from datetime import datetime
from playwright.async_api import async_playwright

async def extract_files_from_page(page):
    """Extracts financial reports, meeting Q&A, and related documents."""
    try:
        financial_sections = await page.query_selector_all("h3.module-financial_year-text")

        for section in financial_sections:
            try:
                # Extract Year from the section heading
                year_text = await section.inner_text()
                year = int(year_text.split()[0]) if year_text.split()[0].isdigit() else None
                
                if not year or year < 2019:
                    print(f"🛑 Stopping: No data required before 2019 ({year})")
                    continue
                
                print(f"📄 Extracting reports for {year}...")

                # Extract 1Q Reports separately
                q1_reports = await section.query_selector_all("div.10Q a.module_link")

                for q1_report in q1_reports:
                    q1_url = await q1_report.get_attribute("href")
                    q1_name = await q1_report.inner_text()

                    # Ensure full URL
                    q1_url = "https:" + q1_url if q1_url.startswith("//") else q1_url

                    # Store Q1 reports separately
                    data_files = [{
                        "file_name": q1_name.strip(),
                        "file_type": "pdf",
                        "date": f"{year}/01/01",
                        "category": "financial_report",
                        "source_url": q1_url,
                        "wissen_url": "unknown"
                    }]

                    file_links_collected.append({
                        "equity_ticker": EQUITY_TICKER,
                        "source_type": "company_financials",
                        "frequency": "quarterly",
                        "event_type": "financial_report",
                        "event_name": q1_name.strip(),
                        "event_date": f"{year}/01/01",
                        "data": data_files
                    })

                    print(f"✅ Extracted: {q1_name}, Year: {year}, URL: {q1_url}")

                # Extract other financial reports in `module_links`
                parent_div = await section.query_selector("div.module_item")
                if parent_div:
                    module_links = await parent_div.query_selector_all("div.module_links a.module_link")

                    for link in module_links:
                        link_url = await link.get_attribute("href")
                        link_name = await link.inner_text()

                        # Ensure full URL
                        link_url = "https:" + link_url if link_url.startswith("//") else link_url

                        # Store additional financial reports
                        data_files = [{
                            "file_name": link_name.strip(),
                            "file_type": "pdf",
                            "date": f"{year}/01/01",
                            "category": "financial_report",
                            "source_url": link_url,
                            "wissen_url": "unknown"
                        }]

                        file_links_collected.append({
                            "equity_ticker": EQUITY_TICKER,
                            "source_type": "company_financials",
                            "frequency": "annual",
                            "event_type": "financial_report",
                            "event_name": link_name.strip(),
                            "event_date": f"{year}/01/01",
                            "data": data_files
                        })

                        print(f"✅ Extracted: {link_name}, Year: {year}, URL: {link_url}")

            except Exception:
                print(f"⚠️ Error processing financial section: {traceback.format_exc()}")

    except Exception:
        print(f"⚠️ Error extracting financial reports: {traceback.format_exc()}")




        # Extract Financial Reports & Meeting Q&A (2019-2025)
        financial_sections = await page.query_selector_all("h3.module-financial_year-text")
        
        for section in financial_sections:
            try:
                year_text = await section.inner_text()
                year = int(year_text.split()[0]) if year_text.split()[0].isdigit() else None
                
                if year and (2019 <= year <= 2025):
                    print(f"📄 Extracting files for {year}...")

                    # Extract all linked financial documents
                    report_links = await section.query_selector_all("div.10Q a.module_link")
                    
                    for report in report_links:
                        report_url = await report.get_attribute("href")
                        report_name = await report.inner_text()

                        # Ensure full URL
                        report_url = "https:" + report_url if report_url.startswith("//") else report_url

                        # Collect report data
                        data_files = [{
                            "file_name": report_name.strip(),
                            "file_type": "pdf",
                            "date": f"{year}/01/01",
                            "category": "financial_report",
                            "source_url": report_url,
                            "wissen_url": "unknown"
                        }]

                        # Append structured financial data
                        file_links_collected.append({
                            "equity_ticker": EQUITY_TICKER,
                            "source_type": "company_financials",
                            "frequency": "annual",
                            "event_type": "financial_report",
                            "event_name": report_name.strip(),
                            "event_date": f"{year}/01/01",
                            "data": data_files
                        })

                        print(f"✅ Extracted: {report_name}, Year: {year}, URL: {report_url}")

            except Exception:
                print(f"⚠️ Error processing financial section: {traceback.format_exc()}")

    except Exception:
        print(f"⚠️ Error extracting files: {traceback.format_exc()}")





async def find_next_page(page):
    """Finds and returns the next page URL if pagination exists."""
    try:
        await page.wait_for_selector("a", timeout=10000)
        all_links = await page.query_selector_all("a")
        for link in all_links:
            text = await link.inner_text()
            if "Next" in text or ">" in text:
                next_page_url = await link.get_attribute("href")
                return urljoin(SEC_FILINGS_URL, next_page_url)
    except Exception as e:
        print(f"⚠️ Error finding next page: {e}")
    return None

async def scrape_sec_filings():
    """Main function to scrape SEC filings."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": SEC_FILINGS_URL
        })

        page = await context.new_page()
        await enable_stealth(page)

        current_url = SEC_FILINGS_URL
        while current_url and current_url and not stop_scraping:
            visited_urls.add(current_url)
            print(f"\n🔍 Visiting: {current_url}")
            try:
                await page.goto(current_url, wait_until="load", timeout=120000)
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight);")
            except Exception as e:
                print(f"⚠️ Failed to load {current_url}: {e}")
                break

            await extract_files_from_page(page)
            await asyncio.sleep(random.uniform(1, 3))  # Human-like delay

            next_page = await find_next_page(page)
            if next_page and not stop_scraping:
                current_url = next_page
            else:
                break

        if file_links_collected:
            with open(JSON_FILENAME, "w", encoding="utf-8") as f:
                json.dump(file_links_collected, f, indent=4)
            print(f"\n✅ File links saved in: {JSON_FILENAME}")
        else:
            print("\n❌ No file links found.")

        await browser.close()

# Run the scraper
asyncio.run(scrape_sec_filings())
