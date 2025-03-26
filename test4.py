import asyncio
from playwright.async_api import async_playwright
from pypdl import Pypdl

import magic
import os

import magic
import os

def add_extension_if_missing(file_path):
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


async def handle_web_page(url):
    async with async_playwright() as p2:
        browser2 = await p2.chromium.launch(headless=True)
        context2 = await browser2.new_context()

        page2 = await context2.new_page()
        print(f"Scraping webpage: {url}")
        await page2.goto(url)

        # Wait for page to load (you can wait for specific elements if necessary)
        await page2.wait_for_load_state('load')

        # Extract all links
        links = await page2.eval_on_selector_all("a", "elements => elements.map(element => element.href)")
        files_meta_data = []

        found=False
        extensions = ['.pdf', '.zip', '.rar', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx']
        for link in links:
            if any(ext in link for ext in extensions):
                found=True
                # Handle PDF links
                url = url.rstrip('/')
                file_name = link.split("/")[-1]
                print('saving file...')
                await asyncio.sleep(2)
                # Download file directly (for .zip, .exe, etc.)
                dl = Pypdl()
                dl.start(url=link, retries=3, file_path=f'downloads/{file_name}', clear_terminal=False, overwrite=True)
                absolute_path = os.path.abspath(f'downloads/{file_name}')
                file_type, absolute_path = add_extension_if_missing(absolute_path)
                files_meta_data.append({'file_type': file_type, "absolute_path": absolute_path, "file_name": file_name})

        if not found:
            # Generate PDF from the page and save it
            url = url.rstrip('/')
            file_name = link.split("/")[-1]
            await page2.pdf(path=f'downloads/{file_name}')
            absolute_path = os.path.abspath(f'downloads/{file_name}')
            file_type, absolute_path = add_extension_if_missing(absolute_path)
            return [{'file_type': file_type, "absolute_path": absolute_path, "file_name": file_name}]
            # Close the browser   

        await browser2.close()
        return files_meta_data

async def download_file(url, output_folder="downloads/"):
    url = url.rstrip('/')
    extensions = ['.pdf', '.zip', '.rar', '.mp4', '.mp3', '.htm', '.mkv', '.avi', '.csv', '.xlsx']
    if any(ext in url for ext in extensions):
        file_name = url.split("/")[-1]
        print('saving file...')
        await asyncio.sleep(2)
        # Download file directly (for .zip, .exe, etc.)
        dl = Pypdl()
        dl.start(url=url, retries=3, file_path=f'downloads/{file_name}', clear_terminal=False, overwrite=True)
        absolute_path = os.path.abspath(f'downloads/{file_name}')
        file_type, absolute_path = add_extension_if_missing(absolute_path)
        return [{'file_type': file_type, "absolute_path": absolute_path, "file_name": file_name}]
    else:
        # If it's a webpage, handle it separately
        lis = await handle_web_page(url)
        return lis

    
# Example usage
urls = [
    # "https://cdn.ferrari.com/cms/network/media/pdf/FNV%20-%20BuyBack%20PR%20March%207%202025%20ENG%20Final.pdf?_gl=1*h89yr2*_ga*MTYzNDMzMjA3My4xNzQyODQyNzM3*_ga_JM1HT9B412*MTc0Mjk3MzM4MS4zLjEuMTc0Mjk3MzYwMy4wLjAuODYzMTgyODkw",  # Direct PDF download
    "https://www.kering.com/en/news/kering-and-les-rencontres-d-arles-to-present-the-2025-women-in-motion-award-for-photography-to-nan-goldin/"
    # "https://example.com/page-with-downloads"  # Webpage with potential downloads
]

a = asyncio.run(download_file("https://www.kering.com/en/news/kering-and-les-rencontres-d-arles-to-present-the-2025-women-in-motion-award-for-photography-to-nan-goldin/"))
# print(add_extension_if_missing('/home/abdulrauf/Projects/fin_scraper/downloads/www.kering.com'))
print(a)