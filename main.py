import asyncio
import sys
import os
from scrapers.Scraper import Scraper
import utils  # Make sure utils/__init__.py exists or import individual functions if needed

def main(config_path):
    scraper = Scraper(utils_module=utils, config_path=config_path)
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
