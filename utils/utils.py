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
    # file_path = os.path.join(download_folder, filename)
    file_path = os.path.abspath(f'downloads/{filename}')

    # Ensure the folder exists
    os.makedirs(download_folder, exist_ok=True)

    attempts = 0
    while attempts < 3:
        try:
            print(f"🔍 Attempt {attempts + 1}: Downloading {url}")

            # Download the file
            response = requests.get(url, timeout=10)  # Added timeout for reliability
            print(f"📡 Response Status: {response.status_code}")

            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Successfully downloaded: {file_path}")

                # Get file type from response headers or infer from filename
                # file_type = response.headers.get('Content-Type')
                # print(f"📄 Detected MIME Type: {file_type}")

                # if file_type:
                #     file_extension = mimetypes.guess_extension(file_type)
                #     if file_extension:
                #         file_type = file_extension.lstrip(".")  # Convert ".pdf" -> "pdf"
                #     else:
                #         file_type = 'html'
                # else:
                #     file_type = os.path.splitext(filename)[1].lstrip(".")  # Extract from filename

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
        logging.error(f"Error adding extension: {e}")
        return None, None

async def extract_links_from_url(url, headless=False):
    try:
        async with async_playwright() as p2:
            browser2 = await p2.chromium.launch(headless=headless)
            context2 = await browser2.new_context()
            page2 = await context2.new_page()
            await enable_stealth(page2)

            logging.info(f"Extracting links from webpage: {url}")
            await page2.goto(url)
            await page2.wait_for_load_state('load')

            if await is_bad_link(page2):
                logging.warning(f"Bad link detected: {url}")
                return None, None

            links = await page2.eval_on_selector_all("a", "elements => elements.map(element => element.href)")
            all_links = [link for link in links if any(ext in link for ext in ['.pdf', '.zip', '.rar', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx'])]

            found = (len(all_links) > 0)
            if not all_links:
                all_links.append(url)

            await browser2.close()
            logging.info(f"Found {len(all_links)} links on {url}")
            return all_links, found
    except:
        logging.info(f"Error extracting links from url: {url}")
        return [url], False
    
    
async def convert_page_to_pdf(url, base_url="https://www.sec.gov", headless=True):
    url = url.rstrip('/')
    file_name = url.split("/")[-1]
    logging.info(f"Downloading file from: {url}")
    try:
        async with async_playwright() as p2:
            browser2 = await p2.chromium.launch(headless=headless)
            context2 = await browser2.new_context()
            page2 = await context2.new_page()
            await enable_stealth(page2)
            
            logging.info(f"Attempting to extract webpage content from: {url}")
            await page2.goto(url)
            await page2.wait_for_load_state('load') 
            await page2.pdf(path=f'downloads/{file_name}')     
            absolute_path = os.path.abspath(f'downloads/{file_name}') 
            file_type, absolute_path = add_extension_if_missing(absolute_path)
            if file_type is None:
                raise Exception("Failed to determine file type")
            logging.info(f"Saved webpage as PDF: {absolute_path}")
            return absolute_path, file_name, file_type 
    except Exception as e:
        logging.error(f"Error processing webpage: {e}")
        return None, None, None


async def download_file(url, base_url="https://www.sec.gov", headless=True):
    url = url.rstrip('/')
    file_name = url.split("/")[-1]
    logging.info(f"Downloading file from: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': base_url,
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    try:
        dl = Pypdl()
        dl.start(url=url, retries=2, file_path=f'downloads/{file_name}', clear_terminal=False, overwrite=True, headers=headers)
        absolute_path = os.path.abspath(f'downloads/{file_name}')
        file_type, absolute_path = add_extension_if_missing(absolute_path)
        logging.info(f"File downloaded: {absolute_path} ({file_type})")
        return absolute_path, file_name, file_type 
    except Exception as e:
        logging.error(f"Can't download file using PYPDL: {e}")
        try:
            return await convert_page_to_pdf(url, base_url, headless)
        except Exception as e:
            logging.error(f"Error Converting webpage to PDF: {e}")
            return None, None, None

async def check_file_link(url):
    if url is None:
        return None
    url = url.rstrip('/')
    logging.info(f"Checking file link: {url}")
    return any(ext in url for ext in ['.pdf', '.zip', '.rar', '.mkv', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx'])



print(asyncio.run(extract_links_from_url('https://event.webcasts.com/starthere.jsp?ei=1683052&tp_key=aaafb48132&tp_special=8')))