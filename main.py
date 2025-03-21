import asyncio
import yaml
import importlib
import sys
from pathlib import Path

# Add 'scrapers' folder to sys.path so that the module can be found
sys.path.append(str(Path(__file__).parent / 'scrapers'))

def load_scraper(scraper_name):
    """Dynamically loads the scraper class based on the scraper name in the config."""
    try:
        # Scraper module (file) name should match the class name in the config
        module = importlib.import_module(f'scrapers.{scraper_name}')  # Import the module using the scraper name
        class_ = getattr(module, scraper_name)  # Get the class from the module
        return class_
    except Exception as e:
        print(f"⚠️ Error loading scraper '{scraper_name}': {e}")
        return None

# Main function to scrape based on the config
async def run_scraper():
    # Load the config file
    config_path = 'config/PVH.yaml'  # Path to the YAML config file (now for all scrapers)
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"⚠️ Configuration file '{config_path}' not found.")
        return
    except yaml.YAMLError as e:
        print(f"⚠️ Error parsing the YAML configuration file: {e}")
        return

    # Iterate over all scraper configurations in the YAML file
    tasks = []
    for scraper_name, scraper_config in config.items():
        print(f"🔍 Running scraper for {scraper_name}...")

        try:
            ticker = scraper_config.get('ticker', '')
            url = scraper_config.get('url', '')
            output_file = scraper_config.get('output', '')
            selectors = scraper_config.get('selectors', {})
            pagination = scraper_config.get('pagination', None)  # Default to None if not found
            defaults = scraper_config.get('defaults', {})
            cutoff_years_back = scraper_config.get('cutoff', {}).get('years_back', 5)

            # Check if all required config fields are present
            if not all([ticker, url, output_file, selectors]):
                print(f"⚠️ Missing essential config for scraper: {scraper_name}. Skipping...")
                continue

            # Load the scraper dynamically
            scraper_class = load_scraper(scraper_config['scraper'])

            if scraper_class is None:
                print(f"⚠️ Could not load scraper class for {scraper_name}. Skipping...")
                continue

            # Initialize the scraper class with the configuration
            scraper = scraper_class(
                base_url=url,  # Pass individual parameters, not the whole config
                output_file=output_file,
                selectors=selectors,
                pagination=pagination,
                defaults=defaults,
                cutoff_years_back=cutoff_years_back
            )

            # Run the scraper for this configuration
            tasks.append(scraper.scrape())

        except Exception as e:
            print(f"⚠️ Error processing scraper {scraper_name}: {e}")

    if tasks:
        # Wait for all scrapers to finish
        await asyncio.gather(*tasks)
    else:
        print("❌ No scrapers to run.")

# Run the main function
if __name__ == "__main__":
    asyncio.run(run_scraper())
