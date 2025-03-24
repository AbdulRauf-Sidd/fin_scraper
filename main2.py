import asyncio
import sys
import os
# from scrapers.Scraper import Scraper
from scrapers.Scraper_all import Scraper
from dotenv import load_dotenv

import utils  # Make sure utils/__init__.py exists or import individual functions if needed
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_path, '.env')
load_dotenv(env_path)


def main(config_path):
    scraper = Scraper(utils_module=utils, config_path=config_path, page='WDAY_events')
    asyncio.run(scraper.scrape())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_file.yaml>")
        sys.exit(1)

    config_file = sys.argv[1]

    if not os.path.exists(config_file):
        print(f"❌ Config file '{config_file}' does not exist.")
        sys.exit(1)

    main(config_file)
