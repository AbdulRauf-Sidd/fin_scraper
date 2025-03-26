import asyncio
from playwright.async_api import async_playwright
from pypdl import Pypdl
from utils.is_bad_link import is_bad_link

import magic
import os

import magic
import os

def add_extension_if_missing(file_path):
    try:

        # Using python-magic to detect the file type
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)

        # Map MIME types to common file extensions
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

        # Get the corresponding extension
        extension = mime_to_extension.get(file_type, '')

        # If the extension is not already present, add it
        if extension and not file_path.endswith(extension):
            new_file_path = file_path + extension
        else:
            new_file_path = file_path

        # Replace the original file with the new file path (if needed)
        if new_file_path != file_path:
            os.rename(file_path, new_file_path)

        # Return the file type (without 'application/' prefix) and the new file path
        return file_type.split('/')[1], file_path
    except:
        print("ERROR ADDING EXTENSION")
        return None, None


async def handle_web_page(url):
    async with async_playwright() as p2:
        browser2 = await p2.chromium.launch(headless=True)
        context2 = await browser2.new_context()

        page2 = await context2.new_page()
        print(f"Extracting links from webpage: {url}")
        await page2.goto(url)

        # Wait for page to load (you can wait for specific elements if necessary)
        await page2.wait_for_load_state('load')

        #TODO INSERT BAD LINK FUNCTION
        if is_bad_link(page2):
            return None, None

        # Extract all links
        links = await page2.eval_on_selector_all("a", "elements => elements.map(element => element.href)")
        all_links = []

        found=False
        extensions = ['.pdf', '.zip', '.rar', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx']
        for link in links:
            if any(ext in link for ext in extensions):
                found=True
                all_links.append(link)
                # Handle PDF links
                # url = url.rstrip('/')
                # file_name = link.split("/")[-1]
                # print('saving file...')
                # await asyncio.sleep(2)
                # Download file directly (for .zip, .exe, etc.)

        if not False:
            all_links.append(url)

        await browser2.close()
        return all_links, found
              

        
async def download_file(url, base_url="https://www.sec.gov", headless=True):
    url = url.rstrip('/')
    file_name = url.split("/")[-1]
    print('saving file...')
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
        # Download file directly (for .zip, .exe, etc.)
        dl = Pypdl()
        dl.start(url=url, retries=2, file_path=f'downloads/{file_name}', clear_terminal=False, overwrite=True, headers=headers)
        absolute_path = os.path.abspath(f'downloads/{file_name}')
        file_type, absolute_path = add_extension_if_missing(absolute_path)
        return [{'file_type': file_type, "absolute_path": absolute_path, "file_name": file_name}]
    except:
        try:
            async with async_playwright() as p2:
                browser2 = await p2.chromium.launch(headless=headless)
                context2 = await browser2.new_context()

                page2 = await context2.new_page()
                print(f"Extracting links from webpage: {url}")
                await page2.goto(url)

                # Wait for page to load (you can wait for specific elements if necessary)
                await page2.wait_for_load_state('load') 
                await page2.pdf(path=f'downloads/{file_name}')     
                absolute_path = os.path.abspath(f'downloads/{file_name}') 
                file_type, absolute_path = add_extension_if_missing(absolute_path)
                if file_type is None:
                    raise Exception
                return [{'file_type': file_type, "absolute_path": absolute_path, "file_name": file_name}]
        except:
            print('ERROR DOWNLOADING FILES: ', url)

    # If it's a webpage, handle it separately
    lis = await handle_web_page(url)
    return lis


async def check_file_link(url):
    url = url.rstrip('/')
    extensions = ['.pdf', '.zip', '.rar', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx']
    if any(ext in url for ext in extensions):
        return True
    return False

    

# a = asyncio.run(download_file("https://d18rn0p25nwr6d.cloudfront.net/CIK-0001506293/943ec678-3a93-4816-94e5-aa6b10d9dcc7.pdf"))
# # print(add_extension_if_missing('/home/abdulrauf/Projects/fin_scraper/downloads/www.kering.com'))
# print(a)
                # dl = Pypdl()
                # dl.start(url=link, retries=3, file_path=f'downloads/{file_name}', clear_terminal=False, overwrite=True)
                # absolute_path = os.path.abspath(f'downloads/{file_name}')
                # file_type, absolute_path = add_extension_if_missing(absolute_path)
                # all_links.append({'file_type': file_type, "absolute_path": absolute_path, "file_name": file_name})
            