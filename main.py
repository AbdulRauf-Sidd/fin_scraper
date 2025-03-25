import asyncio
import sys
import os
from scrapers.Scraper import Scraper
import utils  # Ensure utils/__init__.py exists or import specific functions if needed

async def scrape_config(config_path, page):
    """Runs scraper for a given config file and page."""
    scraper = Scraper(utils_module=utils, config_path=config_path, page=page)
    await scraper.scrape()

async def main(config_files, page):
    """Runs multiple scrapers concurrently."""
    tasks = [scrape_config(config, page) for config in config_files]
    await asyncio.gather(*tasks)  # Run all scraping tasks concurrently

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <config1.yaml> <config2.yaml> ... <page>")
        sys.exit(1)

    *config_files, page = sys.argv[1:]  # Capture all config files, last arg is page

    # Validate config files
    missing_files = [cfg for cfg in config_files if not os.path.exists(cfg)]
    if missing_files:
        print(f"❌ Missing config files: {', '.join(missing_files)}")
        sys.exit(1)

    asyncio.run(main(config_files, page))
