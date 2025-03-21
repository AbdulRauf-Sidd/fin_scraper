from utils.date_utils import accept_cookies, enable_stealth
import json
import asyncio
from playwright.async_api import async_playwright
import spacy
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")

def refine_event_name(raw_name):
    """
    Refine the raw event name extracted by filtering out irrelevant words or fragments.
    Uses SpaCy's part-of-speech tagging to remove non-noun tokens like verbs and adjectives.
    
    Arguments:
    raw_name -- the initially extracted raw event name string.
    
    Returns:
    refined_name -- the filtered event name with only relevant entities.
    """
    # Process the raw name again with SpaCy
    doc = nlp(raw_name)

    # Define a list of irrelevant words or fragments to discard
    discard_keywords = [
        # "view",  
        # "sep", "am", "pm", "edt", "pdt", 
        # "date", "link", "forum", "details"
    ]
    
    # Filter tokens: keep only proper nouns, event-related terms, and named entities
    refined_tokens = [
        token.text for token in doc 
        if (token.pos_ == 'PROPN' or token.pos_ == 'NOUN') and token.text.lower() not in discard_keywords
    ]

    # Reconstruct the refined event name from the remaining tokens
    refined_name = " ".join(refined_tokens)

    # Return a cleaned-up version of the event name
    return refined_name.strip()

def extract_event_name_from_text(text):
    """
    Extract event names from the given HTML or plain text using NLP techniques (SpaCy NER).
    First, remove HTML tags using BeautifulSoup.

    Arguments:
    text -- the input string or list of strings that may contain event information.

    Returns:
    event_name -- extracted event name or None if not found.
    """
    # If the input is a list of strings, combine them
    if isinstance(text, list):
        text = " ".join(text)

    # Clean the HTML tags from the input text (if any)
    soup = BeautifulSoup(text, "html.parser")
    cleaned_text = soup.get_text()

    # Process the cleaned text with SpaCy NLP model
    doc = nlp(cleaned_text)

    # Extract potential event names (using named entities)
    event_names = []
    for ent in doc.ents:
        # We are looking for named entities that might be event names, such as 'ORG', 'EVENT', 'WORK_OF_ART'
        if ent.label_ in ['ORG', 'EVENT', 'WORK_OF_ART', 'CONFERENCE CALL']:  # These labels are more likely to be event-related
            raw_event_name = ent.text.strip()
            refined_event_name = refine_event_name(raw_event_name)
            event_names.append(refined_event_name)

    # If we have multiple event names, deduplicate and choose the most relevant one
    if event_names:
        # Remove duplicates by converting the list to a set, then back to a list
        event_names = list(set(event_names))

        # Choose the longest event name as the most likely candidate (more complete)
        event_name = max(event_names, key=len)
        return event_name.strip()
    
    # If no event name found, return None
    return None

class FlatListScraper:
    def __init__(self, base_url, output_file, selectors, pagination, defaults, cutoff_years_back):
        self.base_url = base_url
        self.output_file = output_file
        self.selectors = selectors
        self.pagination = pagination
        self.defaults = defaults
        self.cutoff_years_back = cutoff_years_back

    async def load_page(self, page, url):
        """Load the page based on the given URL."""
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await accept_cookies(page)  # Accept cookies if present
            await enable_stealth(page)   # Enable stealth mode to evade bot detection
            await asyncio.sleep(5)  # Ensure page content loads
        except Exception as e:
            print(f"⚠️ Error loading page: {e}")

    async def extract_data_from_page(self, page):
        """Extract data from the loaded page."""
        events = []

        # Get event blocks based on the generic selector
        event_blocks = await page.query_selector_all(self.selectors['event_block'])

        # Extract the HTML content of each event block
        for block in event_blocks:
            try:
                # Get the inner HTML of the event block
                event_html = await block.inner_html()
                print('inner HTML: ', (event_html), '\n')
                print('extarcted:', extract_event_name_from_text(event_html))
                print('\n\n')

                # Add a separator after each event block
                events.append(event_html)

            except Exception as e:
                print(f"⚠️ Error extracting HTML from event block: {e}")

        return events

    
    # async def extract_text_from_element(self, block, selector):
    #     """Extract text from any tag within the block using the given selector."""
    #     try:
    #         # Look for the element and get its inner text, even if it's inside different tags
    #         element = await block.query_selector(selector)
    #         if element:
    #             return await element.inner_text()
    #         return "Unknown"  # If no text is found
    #     except Exception as e:
    #         print(f"⚠️ Error extracting text for {selector}: {e}")
    #         return "Unknown"

    # async def extract_links_from_element(self, block, selector):
    #     """Extract all the links from a block, based on the given selector."""
    #     links = []
    #     try:
    #         elements = await block.query_selector_all(selector)
    #         for element in elements:
    #             file_url = await element.get_attribute("href")
    #             if file_url:
    #                 absolute_url = ensure_absolute_url(self.base_url, file_url)
    #                 file_links = {
    #                     "url": absolute_url,
    #                     "file_name": await extract_file_name(absolute_url),
    #                     "file_type": get_file_type(absolute_url)
    #                 }
    #                 links.append(file_links)
    #     except Exception as e:
    #         print(f"⚠️ Error extracting links for {selector}: {e}")
    #     return links

    async def scrape(self):
        """Main function to scrape the data."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print(f"🔍 Visiting: {self.base_url}")
                await self.load_page(page, self.base_url)

                # Extract data from the single page
                events = await self.extract_data_from_page(page)

                if events:
                    # Process and save events
                    with open(self.output_file, "w", encoding="utf-8") as f:
                        json.dump(events, f, indent=4)
                    print(f"\n✅ Data saved in: {self.output_file}")
                else:
                    print("\n❌ No events found.")
            
            except Exception as e:
                print(f"⚠️ Error: {e}")

            await browser.close()