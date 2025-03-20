import yaml
from scrapers.flatlist_scraper import FlatListScraper
from scrapers.detailpage_scraper import DetailPageScraper
from scrapers.tablescraper import TableScraper

# Load config from YAML file
def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def main():
    equity_ticker = "PVH_news"  # Example ticker
    config_file = f"config/{equity_ticker}.yaml"  # Load specific config file
    config = load_config(config_file)

    # Initialize scraper based on configuration
    if config['scraper'] == 'FlatListScraper':
        scraper = FlatListScraper(config, db_client, cloudflare_client)
    elif config['scraper'] == 'DetailPageScraper':
        scraper = DetailPageScraper(config, db_client, cloudflare_client)
    elif config['scraper'] == 'TableScraper':
        scraper = TableScraper(config, db_client, cloudflare_client)

    # Assuming we have a page object
    scraper.scrape(page)

if __name__ == "__main__":
    main()
