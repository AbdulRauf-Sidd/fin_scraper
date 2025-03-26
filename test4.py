import asyncio
import logging
import os
from playwright.async_api import async_playwright
from pypdl import Pypdl
from utils.is_bad_link import is_bad_link
import magic

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

async def handle_web_page(url):
    async with async_playwright() as p2:
        browser2 = await p2.chromium.launch(headless=True)
        context2 = await browser2.new_context()
        page2 = await context2.new_page()
        
        logging.info(f"Extracting links from webpage: {url}")
        await page2.goto(url)
        await page2.wait_for_load_state('load')

        if is_bad_link(page2):
            logging.warning(f"Bad link detected: {url}")
            return None, None

        links = await page2.eval_on_selector_all("a", "elements => elements.map(element => element.href)")
        all_links = [link for link in links if any(ext in link for ext in ['.pdf', '.zip', '.rar', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx'])]
        
        if not all_links:
            all_links.append(url)
        
        await browser2.close()
        logging.info(f"Found {len(all_links)} links on {url}")
        return all_links, bool(all_links)

async def download_file(url, base_url="https://www.sec.gov", headless=True):
    url = url.rstrip('/')
    file_name = url.split("/")[-1]
    logging.info(f"Downloading file from: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
        'Referer': base_url
    }
    try:
        dl = Pypdl()
        dl.start(url=url, retries=2, file_path=f'downloads/{file_name}', clear_terminal=False, overwrite=True, headers=headers)
        absolute_path = os.path.abspath(f'downloads/{file_name}')
        file_type, absolute_path = add_extension_if_missing(absolute_path)
        logging.info(f"File downloaded: {absolute_path} ({file_type})")
        return [{'file_type': file_type, "absolute_path": absolute_path, "file_name": file_name}]
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        try:
            async with async_playwright() as p2:
                browser2 = await p2.chromium.launch(headless=headless)
                context2 = await browser2.new_context()
                page2 = await context2.new_page()
                
                logging.info(f"Attempting to extract webpage content from: {url}")
                await page2.goto(url)
                await page2.wait_for_load_state('load') 
                await page2.pdf(path=f'downloads/{file_name}')     
                absolute_path = os.path.abspath(f'downloads/{file_name}') 
                file_type, absolute_path = add_extension_if_missing(absolute_path)
                if file_type is None:
                    raise Exception("Failed to determine file type")
                logging.info(f"Saved webpage as PDF: {absolute_path}")
                return [{'file_type': file_type, "absolute_path": absolute_path, "file_name": file_name}]
        except Exception as e:
            logging.error(f"Error processing webpage: {e}")
    
    lis = await handle_web_page(url)
    return lis

async def check_file_link(url):
    url = url.rstrip('/')
    logging.info(f"Checking file link: {url}")
    return any(ext in url for ext in ['.pdf', '.zip', '.rar', '.mkv', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx'])
