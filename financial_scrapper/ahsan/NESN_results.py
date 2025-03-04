import requests
import time

# ZenRows API Key and URL
apikey = 'YOUR_API_KEY_HERE'  # Replace with your actual API key
url = 'https://www.nestle.com/investors/results'

# ZenRows parameters
params = {
    'url': url,
    'apikey': apikey,
    'js_render': 'true',
    'premium_proxy': 'true',
    'outputs': 'links',  # Request all links from the page
}

# Initial page scraping request
response = requests.get('https://api.zenrows.com/v1/', params=params)

if response.status_code == 200:
    links = response.json().get('links', [])
    print(f"Found {len(links)} links on the page.")

    # Function to check if URL is valid (not a fragment)
    def is_valid_url(link):
        return link.startswith('http://') or link.startswith('https://')

    # Optionally, scrape each linked page with retry logic
    for link in links:
        if not is_valid_url(link):
            print(f"Skipping invalid URL: {link}")
            continue
        
        print(f"Scraping linked page: {link}")
        
        # ZenRows parameters for linked pages
        link_params = {
            'url': link,
            'apikey': apikey,
            'js_render': 'true',
            'premium_proxy': 'true',
            'outputs': 'content',  # You can customize the output as needed
        }

        # Retry logic for failed connections
        attempts = 0
        while attempts < 3:
            try:
                link_response = requests.get('https://api.zenrows.com/v1/', params=link_params)
                if link_response.status_code == 200:
                    print(f"Successfully scraped: {link}")
                    break  # Successfully scraped, break out of the retry loop
                else:
                    print(f"Failed to scrape {link}: {link_response.text}")
                    break  # You can choose to retry here if needed
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error when trying to scrape {link}: {e}")
                attempts += 1
                time.sleep(2 ** attempts)  # Exponential backoff

else:
    print(f"Failed to scrape initial page: {response.text}")