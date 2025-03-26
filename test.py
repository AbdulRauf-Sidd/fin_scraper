from pypdl import Pypdl
from utils.utils import add_extension_if_missing, convert_page_to_pdf
import os 
import asyncio


async def download_file(url, base_url="https://www.sec.gov", headless=True):
    url = url.rstrip('/')
    file_name = url.split("/")[-1]
    # logging.info(f"Downloading file from: {url}")
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
        dl.start(url=url, retries=2, file_path=f'test_docs/{file_name}', clear_terminal=False, overwrite=True, headers=headers)
        absolute_path = os.path.abspath(f'test_docs/{file_name}')
        file_type, absolute_path = add_extension_if_missing(absolute_path)
        # logging.info(f"File downloaded: {absolute_path} ({file_type})")
        return absolute_path, file_name, file_type 
    except Exception as e:
        # logging.error(f"Can't download file using PYPDL: {e}")
        try:
            return await convert_page_to_pdf(url, base_url, headless)
        except Exception as e:
            # logging.error(f"Error Converting webpage to PDF: {e}")
            return None, None, None
        
asyncio.run(download_file(url='https://www.pvh.com/news/press-releases/PVH-Corp-to-Host-Conference-Call-to-Discuss-Fourth-Quarter-and-YearEnd-2024-Earnings-Results', headless=False))