import requests

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        # 'Referer': 'https://www.sec.gov',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

with requests.Session() as s:
    s.headers.update(headers)
    response = s.get('https://www.reckitt.com/media/lwvnxpao/reckitt-agm-nom-2025.pdf')

    if response.status_code == 200:
        with open('output.pdf', 'wb') as f:
            f.write(response.content)
        print("PDF downloaded successfully.")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
