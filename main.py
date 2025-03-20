import asyncio
import yaml
import importlib
import sys
from pathlib import Path

# Add 'scrapers' folder to sys.path so that the module can be found
sys.path.append(str(Path(__file__).parent / 'scrapers'))

def load_scraper(scraper_name):
    """Dynamically loads the scraper class based on the scraper name in the config."""
    module = importlib.import_module(scraper_name)  # Import the module using the scraper name
    class_ = getattr(module, scraper_name)  # Get the class from the module
    return class_

# Main function to scrape based on the config
async def run_scraper():
    # Load the config file
    config_path = 'config/PVH_news.yaml'  # Path to the YAML config file
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Read scraper settings
    scraper_config = config['PVH_news']
    ticker = scraper_config['ticker']
    scraper_name = scraper_config['scraper']
    url = scraper_config['url']
    output_file = scraper_config['output']
    selectors = scraper_config['selectors']
    pagination = scraper_config['pagination']
    defaults = scraper_config['defaults']
    cutoff_years_back = scraper_config['cutoff']['years_back']

    # Load the scraper dynamically
    scraper_class = load_scraper(scraper_name)
    scraper = scraper_class(
        base_url=url,
        output_file=output_file,
        selectors=selectors,
        pagination=pagination,
        defaults=defaults,
        cutoff_years_back=cutoff_years_back
    )

    # Run the scraper
    await scraper.scrape()

# Run the main function
if __name__ == "__main__":
    asyncio.run(run_scraper())
