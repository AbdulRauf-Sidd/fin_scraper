from bs4 import BeautifulSoup
import cloudscraper

# create a cloudscraper instance
scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "linux",
    },
)

# specify the target URL
url = "https://www.nestle.com/investors/results"

# request the target website
response = scraper.get(url)

# get the response status code
print(f"The status code is {response.status_code}")

# parse the returned HTML
soup = BeautifulSoup(response.text, "html.parser")

# get the description element
page_description = soup.select_one(".font-semibold.text-display-md.leading-display-md")

# print the description text
print(page_description.text)
