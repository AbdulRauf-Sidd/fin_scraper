from abc import ABC, abstractmethod
import requests
from datetime import datetime
import os
import time

class AbstractScraper(ABC):
    def __init__(self, config, db_client, cloudflare_client):
        """
        Initialize the scraper with the config, MongoDB, and Cloudflare clients.
        
        :param config: The configuration loaded from the YAML file.
        :param db_client: MongoDB client for storing data.
        :param cloudflare_client: Client to interact with Cloudflare R2.
        """
        self.config = config
        self.db_client = db_client
        self.cloudflare_client = cloudflare_client
        self.data_collection = []

    @abstractmethod
    def download_pdf(self, url, save_to):
        pass

    @abstractmethod
    def accept_cookies(self, page):
        pass

    @abstractmethod
    def find_next_page(self, page):
        pass

    @abstractmethod
    def find_element(self, page, selector):
        pass

    @abstractmethod
    def extract_date_from_text(self, text):
        pass

    @abstractmethod
    def format_date(self, date):
        pass

    @abstractmethod
    def find_href(self, page, selector):
        pass

    @abstractmethod
    def extract_text_from_div(self, div):
        pass

    def process_data(self, event_name, event_date, file_url, event_type, category):
        """
        Process and store the scraped data in the appropriate format.
        """
        file_name = os.path.basename(file_url)
        file_type = file_url.split('.')[-1]
        formatted_date = self.format_date(event_date)

        event_data = {
            "event_name": event_name,
            "event_date": formatted_date,
            "file_name": file_name,
            "file_type": file_type,
            "category": category,
            "source_url": file_url,
            "r2_path": f"{self.config['ticker']}/{formatted_date}/{file_name}/{file_name}.{file_type}",
            "url": f"https://{self.config['cloudflare_r2_url']}/{self.config['ticker']}/{formatted_date}/{file_name}/{file_name}.{file_type}",
            "content_type": self.config.get('defaults', {}).get('event_type', 'unknown')
        }

        # Store data in MongoDB
        self.save_to_db(event_data)

        # Add to the data collection
        self.data_collection.append(event_data)

    def save_to_db(self, event_data):
        """
        Save the event data into MongoDB.

        :param event_data: The data to be saved to the database.
        """
        # MongoDB logic here
        pass

    def upload_to_cloudflare(self, file_path, r2_path):
        """
        Upload the file to Cloudflare R2 storage.

        :param file_path: The local file path.
        :param r2_path: The target path in Cloudflare R2.
        """
        # Cloudflare R2 upload logic here
        pass

    def scrape(self, page):
        """
        Scrape the data according to the configuration.
        """
        event_blocks = page.query_selector_all(self.config['selectors']['event_block'])
        for event_block in event_blocks:
            # Extract event name, date, and other data using the config
            event_name = self.find_element(event_block, self.config['selectors']['event_name'])
            event_date_text = self.find_element(event_block, self.config['selectors']['event_date'])
            event_date = self.extract_date_from_text(event_date_text)
            file_links = self.find_href(event_block, self.config['selectors']['file_links'])

            # Process the extracted data
            self.process_data(event_name, event_date, file_links, self.config['defaults']['event_type'], self.config['selectors']['event_category'])
