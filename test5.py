from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time
import random

def save_page_as_pdf_with_stealth(url, file_path):
    with sync_playwright() as p:
        # Launch browser with stealth capabilities
        browser = p.chromium.launch(headless=False)  # Set headless=True to not display the browser
        page = browser.new_page()

        # Apply stealth to make it less detectable
        stealth_sync(page)

        # Set custom headers (mimicking a real browser)
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': url,  # You can set the Referer as the current URL or as needed
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        
        # Navigate to the URL
        page.on("download", lambda download: download.save_as('downloads/'))
        page.goto(url)
        page.wait_for_load_state('load')

        time.sleep(random.uniform(1, 2))
        # Save the page as a PDF
        # page.pdf(path=file_path)
        
        print(f"PDF saved to {file_path}")
        
        # Close the browser
        browser.close()

# Example usage
url = 'https://www.sec.gov/Archives/edgar/data/21344/000087666120000786/KO8A091820.pdf'  # Replace with the URL you want to save as PDF
file_path = './example_page.pdf'  # Path to save the PDF

save_page_as_pdf_with_stealth(url, file_path)
