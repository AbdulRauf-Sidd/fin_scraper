import asyncio
from urllib.parse import urlparse
import os
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import logging
from pypdl import Pypdl
from utils.is_bad_link import is_bad_link
import magic
from pathlib import Path
import requests
import time


# from utils.is_bad_link import is_bad_link
async def load_page(page, url):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
            await accept_cookies(page)
            await enable_stealth(page)
            
        except Exception as e:
            print(f"⚠️ Error loading page: {e}")


async def accept_cookies(page):
    """Accepts cookies if a consent banner appears."""
    try:
        cookie_button = await page.query_selector("button:has-text('Accept')")
        if cookie_button:
            await cookie_button.click()
            await asyncio.sleep(2)  # Wait to ensure banner disappears
            print("✅ Accepted cookies.")
    except Exception as e:
        print(f"⚠️ No cookie consent banner found or error clicking it: {e}")

async def enable_stealth(page):
    """Inject JavaScript to evade bot detection."""
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    ###############################################
    # UNCOMMENT IF NEW IMPLEMENTATION DOESN'T WORK
    ###############################################
async def download_file_direct(url, download_folder='downloads/'):
    """Download a file from the given URL and save it to the specified folder.
    
    Returns:
        file_path (str): The full path of the downloaded file.
        filename (str): The name of the file.
        file_type (str): The file extension (e.g., "pdf", "docx").
    """
    url = url.rstrip('/')
    filename = os.path.basename(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': "https://www.sec.gov/",
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    # file_path = os.path.join(download_folder, filename)
    file_path = os.path.abspath(f'downloads/{filename}')

    # Ensure the folder exists
    os.makedirs(download_folder, exist_ok=True)

    attempts = 0
    while attempts < 2:
        try:
            print(f"🔍 Attempt {attempts + 1}: Downloading {url}")

            # Download the file
            response = requests.get(url, timeout=10, headers=headers)  # Added timeout for reliability
            print(f"📡 Response Status: {response.status_code}")
            if response.status_code == 200:
                # Try to extract filename from Content-Disposition header (if available)
                content_disposition = response.headers.get('Content-Disposition')
                if content_disposition:
                    # Extract the filename from the header (if present)
                    filename = content_disposition.split("filename=")[-1].strip('\"')
                else:
                    # If no filename is provided in the header, use the URL or a default name
                    filename = url.split("/")[-1]  # Extract filename from URL (default)
    
                # Save the content to the file
                with open(f'{download_folder}/{filename}', 'wb') as f:
                    f.write(response.content)
                print(f"✅ Successfully downloaded: {filename}")

                file_type, file_path = add_extension_if_missing(file_path)

                print(f"🗂️ Final File Type: {file_type}")
                return file_path, filename, file_type
            
            else:
                print(f"⚠️ Failed to download {url}, HTTP Status: {response.status_code}")
                return None, None, None

        except requests.RequestException as e:
            attempts += 1
            print(f"❌ Attempt {attempts}: Request error - {str(e)}")
            if attempts < 3:
                print("🔄 Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("⛔ Maximum retry attempts reached, failed to download.")
                return None, None, None

# async def download_file(url, output_folder="downloads"):
#     """
#     Returns:
#         file_path (str): The full path of the downloaded file.
#         filename (str): The name of the file.
#         file_type (str): The file extension (e.g., "pdf", "docx").
#     """
#     url = url.rstrip('/')
#     filename = os.path.basename(url)
#     file_path = Path(output_folder) / filename
#     abs_path = str(file_path.resolve())

#     # Ensure the folder exists
#     os.makedirs(output_folder, exist_ok=True)

#     # Check for bad link
#     # # is_bad_link = await is_bad_link(url)
#     # if is_bad_link:
#     #     print(f"⛔ Bad link detected: {url}")
#     #     return None, None, None

#     print(f"🔍 Visiting: {url}")
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=False)
#             context = await browser.new_context(
#                 user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
#                 extra_http_headers={
#                     "Accept-Language": "en-US,en;q=0.9",
#                     "Referer": "https://www.sec.gov/",
#                 }
#             )
#             page = await context.new_page()
#             await page.goto(url, wait_until="domcontentloaded")

#             content = await page.content()
#             with open(abs_path, "w", encoding="utf-8") as f:
#                 f.write(content)

#             await browser.close()
#     except Exception as e:
#         print(f"❌ Failed to download {url}: {e}")
#         return None, None, None

#     print(f"✅ Successfully downloaded: {abs_path}")

#     # Determine file type
#     mime_type, _ = mimetypes.guess_type(abs_path)
#     if mime_type:
#         ext = mimetypes.guess_extension(mime_type)
#         file_type = ext.lstrip(".") if ext else file_path.suffix.lstrip(".")
#     else:
#         file_type = file_path.suffix.lstrip(".")

#     if not file_type:
#         file_type = "HTML"
        
#     print(f"📄 Detected MIME Type: {mime_type}")
#     print(f"🗂️ Final File Type: {file_type}")

#     return abs_path, filename, file_type

def join_url(base_url, href):
    if href is None:
        return None
    # Check if the href is already an absolute URL
    if urlparse(href).scheme:
        return href  # Return the href directly as it's already absolute
    
    # Otherwise, join the base_url with the href
    return urljoin(base_url, href)


# asyncio.run(download_file('https://www.kering.com/en/news/kering-and-les-rencontres-d-arles-to-present-the-2025-women-in-motion-award-for-photography-to-nan-goldin/'))


#---------------------------------------V2.0 ------------------------------------
# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/download_file-script.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def add_extension_if_missing(file_path):
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        
        mime_to_extension = {
            'application/pdf': '.pdf',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar',
            'video/mp4': '.mp4',
            'audio/mpeg': '.mp3',
            'text/html': '.htm',
            'text/html': '.html',
            'video/x-matroska': '.mkv',
            'video/x-msvideo': '.avi',
            'text/csv': '.csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx'
        }

        extension = mime_to_extension.get(file_type, '')

        if extension and not file_path.endswith(extension):
            new_file_path = file_path + extension
            os.rename(file_path, new_file_path)
            logging.info(f"Renamed file {file_path} to {new_file_path}")
        else:
            new_file_path = file_path

        return file_type.split('/')[1], new_file_path
    except Exception as e:
        print(e)
        logging.error(f"Error adding extension: {e}")
        return None, None

async def extract_links_from_url(page, url):
    try:

        logging.info(f"Extracting links from webpage: {url}")
        await page.goto(url)
        await enable_stealth(page)
        await page.wait_for_load_state('load')
        # if await is_bad_link(page2):
        #     logging.warning(f"Bad link detected: {url}")
        #     return None, None
        links = await page.eval_on_selector_all("a", "elements => elements.map(element => element.href)")
        all_links = [link for link in links if any(ext in link for ext in ['.pdf', '.zip', '.rar', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx'])]
        found = (len(all_links) > 0)
        # if not all_links:
        #     all_links.append(url)
        # await page.close()
        logging.info(f"Found {len(all_links)} links on {url}")
        return all_links, found
    except:
        await page.close()
        print('ERROR LOGGING')
        logging.info(f"Error extracting links from url: {url}")
        return [url], False
    
    
# async def convert_page_to_pdf(url, base_url="https://www.sec.gov", headless=True):
#     url = url.rstrip('/')
#     file_name = url.split("/")[-1]

#     # Set up logging
#     logging.basicConfig(level=logging.INFO)
#     logging.info(f"Downloading file from: {url}")

#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=headless)
#             context = await browser.new_context()
#             page = await context.new_page()

#             # Check if the URL is a direct PDF link
#             if url.lower().endswith('.pdf'):
#                 logging.info("Direct PDF link detected. Downloading file...")
#                 response = await page.goto(url)
#                 pdf_content = await response.body()
#                 os.makedirs('downloads', exist_ok=True)
#                 file_path = os.path.join('downloads', file_name)
#                 with open(file_path, 'wb') as pdf_file:
#                     pdf_file.write(pdf_content)
#             else:
#                 # Handle as regular HTML page
#                 logging.info(f"Attempting to extract webpage content from: {url}")
#                 await page.goto(url)
#                 await page.wait_for_load_state('load') 
#                 await asyncio.sleep(7)  # Adjust sleep time as necessary
#                 file_path = f'downloads/{file_name}.pdf'
#                 await page.pdf(path=file_path)

#             absolute_path = os.path.abspath(file_path)
#             file_type = 'application/pdf'  # Assuming PDF for both direct downloads and conversions
#             logging.info(f"Saved file as PDF: {absolute_path}")
#             return absolute_path, file_name, file_type 
#     except Exception as e:
#         logging.error(f"Error processing webpage: {e}")
#         return None, None, None

async def capture_full_page_screenshot(context, page=None, url=None):
    url = url.rstrip('/')
    file_name = url.split("/")[-1] + ".png"

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Capturing screenshot from: {url}")

    try:
        if page is None:
            page = await context.new_page()
            logging.info(f"Opening page: {url}")
            await page.goto(url)
            await page.wait_for_load_state('load')
            await asyncio.sleep(2)  # Adjust sleep time as necessary
        # Navigate to the URL
        # Create downloads directory if it does not exist
        os.makedirs('downloads', exist_ok=True)
        file_path = os.path.join('downloads', file_name)
        # Take a full page screenshot
        logging.info("Taking full page screenshot...")
        await page.screenshot(path=file_path, full_page=True)
        absolute_path = os.path.abspath(file_path)
        file_type = 'png'
        logging.info(f"Saved screenshot: {absolute_path}")
        if page is None:
            await page.close()
        return absolute_path, file_name, file_type, 'screenshot'
    except Exception as e:
        await page.close()
        logging.error(f"Error capturing screenshot: {e}")
        return None, None, None, None


async def download_file(context, url, session=None):
    url = url.rstrip('/')
    # file_name = url.split("/")[-1]
    logging.info(f"Downloading file from: {url}")
    try:
        response = session.get(url, timeout=15)  # Added timeout for reliability
        print(f"📡 Response Status: {response.status_code}")
        if 200 <= response.status_code < 300:
            # Try to extract filename from Content-Disposition header (if available)
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition:
                # Extract the filename from the header (if present)
                filename = content_disposition.split("filename=")[-1].strip('\"')
            else:
                # If no filename is provided in the header, use the URL or a default name
                filename = url.split("/")[-1]  # Extract filename from URL (default)

            # Save the content to the file
            with open(f'downloads/{filename}', 'wb') as f:
                f.write(response.content)
            print(f"✅ Successfully downloaded: {filename}")
        else:
            print(f"⚠️ Failed to download file. HTTP Status: {response.status_code}")
            raise Exception("Fall back to pdf")
        absolute_path = os.path.abspath(f'downloads/{filename}')
        file_type, absolute_path = add_extension_if_missing(absolute_path)
        if file_type == 'octet-stream':
            raise Exception("Fall back to pdf")
        print('file type:', file_type)
        logging.info(f"File downloaded: {absolute_path} ({file_type})")
        return absolute_path, filename, file_type, 'download'
    except Exception as e:
        logging.error(f"Can't download file using PYPDL: {e}")
        try:
            return await capture_full_page_screenshot(context, url)
        except Exception as e:
            logging.error(f"Error Capturing Screenshot: {e}")
            return None, None, None, None

async def check_file_link(url):
    if url is None:
        return None
    url = url.rstrip('/')
    logging.info(f"Checking file link: {url}")
    return any(ext in url for ext in ['.pdf', '.zip', '.rar', '.mkv', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx'])


import requests

def create_session(base_url='https://www.sec.gov'):
    """Create a new session with custom headers and settings."""
    # Initialize the session
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': base_url,
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    session = requests.Session()
    session.headers.update(headers)
    return session


async def setup_browser(headless=True):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context()
    page = await context.new_page()
    await enable_stealth(page)
    # Return both playwright and context to manage them outside
    return playwright, browser, context, page

# print(asyncio.run(extract_links_from_url('https://event.webcasts.com/starthere.jsp?ei=1683052&tp_key=aaafb48132&tp_special=8')))