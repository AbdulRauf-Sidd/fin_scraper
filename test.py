from pypdl import Pypdl
from utils.utils import add_extension_if_missing, capture_full_page_screenshot
import os 
import asyncio
import requests


async def download_file(url, base_url="https://www.sec.gov", headless=False):
    url = url.rstrip('/')
    file_name = url.split("/")[-1]
    # logging.info(f"Downloading file from: {url}")
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
    try:
        # dl = Pypdl()
        # dl.start(url=url, retries=2, file_path=f'test_docs/{file_name}', clear_terminal=False, overwrite=True, headers=headers)
        response = requests.get(url, timeout=15, headers=headers)  # Added timeout for reliability
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

            if os.path.exists(f'test_docs/{filename}'):
                print(f"File {filename} already exists. Replacing it...")
                os.remove(f'test_docs/{filename}')
            # Save the content to the file
            with open(f'test_docs/{filename}', 'wb') as f:
                f.write(response.content)
            print(f"✅ Successfully downloaded: {file_name}")
        print('downloaded')
        absolute_path = os.path.abspath(f'test_docs/{filename}')
        file_type, absolute_path = add_extension_if_missing(absolute_path)
        if file_type == 'octet-stream':
            raise Exception("Fall back to pdf")
        print('file type:', file_type)
        # logging.info(f"File downloaded: {absolute_path} ({file_type})")
        return absolute_path, file_name, file_type 
    except Exception as e:
        # logging.error(f"Can't download file using PYPDL: {e}")
        pass 
        
        
asyncio.run(download_file(url=
"https://www.heinekenholding.com/sites/heinekenholding-v2/files/2025-02/heineken-holding-nv-annual-report-2024-final-20250219.pdf"
, headless=False, base_url='https://www.reckitt.com'))
