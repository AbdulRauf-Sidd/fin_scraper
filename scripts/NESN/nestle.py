import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UTILS")))

from utils import *

def get_cloudflare_cookies(url):
    """
    Retrieve Cloudflare cookies for a given URL by calling the local endpoint.
    
    Args:
        url (str): The target URL to get Cloudflare cookies for
    
    Returns:
        dict: A dictionary containing cookies and user agent
    """
    endpoint = "http://localhost:8000/cookies"
    
    try:
        # Make a GET request to the local endpoint
        response = requests.get(endpoint, params={'url': url}, timeout=30)
        
        # Raise an exception for bad responses
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        return data
    
    except requests.RequestException as e:
        print(f"Error retrieving Cloudflare cookies: {e}")
        return None

def fetch_webpage_with_cookies(url):
    """
    Fetch webpage content using Cloudflare bypass cookies.
    
    Args:
        url (str): The target URL to fetch
    
    Returns:
        str: HTML content of the webpage, or None if an error occurs
    """
    # Get Cloudflare cookies
    # cookie_data = get_cloudflare_cookies(url)
    
    # if not cookie_data:
        # print("Failed to retrieve Cloudflare cookies")
        # return None
    
    try:
        # Prepare headers with user agent
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        
        # Prepare cookies
        cookies = {
            'cf_clearance': "SJHuYhHrTZpXDUe8iMuzEUpJxocmOW8ougQVS0.aK5g-1723665177-1.0.1.1-5_NOoP19LQZw4TQ4BLwJmtrXBoX8JbKF5ZqsAOxRNOnW2rmDUwv4hQ7BztnsOfB9DQ06xR5hR_hsg3n8xteUCw",
        }
        
        # Make the request to the target URL
        response = requests.get(url=f"http://localhost:8000/html?url={url}", cookies=cookies, headers=headers, timeout=30)
        
        # Raise an exception for bad responses
        response.raise_for_status()
        
        # Return the HTML content
        return response.text
    
    except requests.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return None
    
def parse_press_releases(html_content):
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all table rows
    rows = soup.find_all('tr')
    
    # List to store events
    events = []
    
    # Loop through rows
    for row in rows:
        # Find title and link
        title_cell = row.find('td', class_='views-field-title')
        if not title_cell:
            continue
        
        link_element = title_cell.find('a')
        if not link_element:
            continue
        
        # Find date cell
        date_cell = row.find('td', class_='views-field-published-at')
        if not date_cell:
            continue
        
        time_element = date_cell.find('time')
        if not time_element:
            continue
        
        # Extract event details
        event_name = link_element.text.strip()
        href = link_element.get('href', '')
        
        # Parse datetime
        datetime_str = time_element.get('datetime', '')
        try:
            # Parse the datetime
            event_date = datetime.fromisoformat(datetime_str.replace('+01:00', ''))
            formatted_date = event_date.strftime('%Y/%m/%d')
        except ValueError:
            # Fallback to the displayed date
            try:
                event_date = datetime.strptime(time_element.text.strip(), '%b %d, %Y')
                formatted_date = event_date.strftime('%Y/%m/%d')
            except ValueError:
                formatted_date = ''
        
        # Construct event JSON
        event = {
            "equity_ticker": "NESN",  # Nestle's ticker symbol
            "source_type": "company_information",
            "frequency": "non-periodic",
            "event_type": "press release",
            "event_name": event_name,
            "event_date": formatted_date,
            "data": [
                {
                    "file_name": href,
                    "file_type": "html",
                    "date": formatted_date,
                    "category": "report",
                    "source_url": "https://www.nestle.com" + href,
                    "wissen_url": "https://www.nestle.com" + href
                }
            ]
        }
        
        events.append(event)
    
    return events

def press_release_scraper():
    # Global list to store all events
    all_events = []
    
    # Base URL with pagination
    base_url = "https://www.nestle.com/investors/pressreleases?page=%2C%2C%2C%2C%2C{}"
    
    # Loop through pages 0 to 50
    for page_num in range(2):  # 0 to 50 inclusive
        try:
            # Construct the URL for the current page
            target_url = base_url.format(page_num)
            
            print(f"Scraping page: {target_url}")
            
            # Fetch the webpage content
            html_content = fetch_webpage_with_cookies(target_url)
            
            if html_content:
                # Parse press releases on this page
                events = parse_press_releases(html_content)
                
                # Add events to the global list
                all_events.extend(events)
                
                # Optional: Print number of events found on this page
                print(f"Found {len(events)} events on page {page_num}")
            
            else:
                print(f"Failed to retrieve content for page {page_num}")
        
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
    
    # After scraping all pages, dump to JSON file
    output_file = "nesn_press.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_events, f, indent=2, ensure_ascii=False)
    
    print(f"Total events scraped: {len(all_events)}")
    print(f"Events saved to {output_file}")
    


    return all_events

def parse_events_calendar(html_content):
    """
    Parse the events calendar HTML and extract event details
    
    Args:
        html_content (str): HTML content of the events calendar page
    
    Returns:
        list: List of event dictionaries
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all table containers
    table_containers = soup.find_all('div', class_='tableContainer')
    
    all_events = []
    
    for container in table_containers:
        # Extract year from the first row
        year_span = container.find('tr', class_='Default-Nestle-TableTableHeaderRow').find('span')
        year = year_span.text.strip() if year_span else None
        
        # If year is less than 2019, stop processing
        if year and int(year) < 2019:
            break
        
        # Find all rows in the table
        rows = container.find_all('tr', class_=re.compile(r'Default-Nestle-TableTableOddRow|Default-Nestle-TableTableEvenRow'))
        
        for row in rows:
            # Find link and date
            link_span = row.find('span')
            date_span = row.find_all('span')[-1]
            
            if link_span and date_span:
                event_name = link_span.text.strip()
                event_date_str = date_span.text.strip()
                event_name2 = extract_euro_event_name(datetime.strptime(event_date_str, "%b %d, %Y").strftime("%Y/%m/%d"), event_name)
                # Find href
                link = row.find('a')
                if link:
                    href = link.get('href', '')

                    print(datetime.strptime(event_date_str, "%b %d, %Y").strftime("%Y/%m/%d"))

                    event_type = classify_euro_periodic_type(event_name, href)
                    if event_name2:
                        event_name = event_name2
                    
                    # Create event dictionary
                    event = {
                        "equity_ticker": "NESN",
                        "source_type": "company_information",
                        "frequency": "periodic",
                        "event_type": event_type,
                        "event_name": event_name,
                        "event_date": datetime.strptime(event_date_str, "%b %d, %Y").strftime("%Y/%m/%d"),
                        "year": year,
                        "href": f"https://www.nestle.com{href}",
                        "data": []
                    }
                    
                    all_events.append(event)
    
    return all_events

def extract_data_files(event_url):
    """
    Extract data files from an event page
    
    Args:
        event_url (str): URL of the event page
    
    Returns:
        list: List of data file dictionaries
    """
    try:
        # Fetch the event page content
        html_content = fetch_webpage_with_cookies(event_url)
        
        if not html_content:
            print(f"Failed to fetch content for {event_url}")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all links
        links = soup.find_all('a', href=re.compile(r'\.(pdf|xlsx?|csv|docx?)$'))
        
        data_files = []
        for link in links:
            file_url = link.get('href', '')
            
            # Ensure full URL
            if not file_url.startswith('http'):
                file_url = f"https://www.nestle.com{file_url}"
            
            # Extract file details
            file_name = link.text.strip() or link.get('download') or file_url.split('/')[-1]
            file_type = file_url.split('.')[-1].lower()
            
            data_files.append({
                "file_name": file_name,
                "file_type": file_type,
                "source_url": file_url,
                "wissen_url": 'null',
                "category": "report"
            })
        
        return data_files
    
    except Exception as e:
        print(f"Error extracting data files from {event_url}: {e}")
        return []

def comprehensive_nestle_event_scraper():
    """
    Comprehensive scraper for Nestle events and their associated data files
    """
    # Target URL for events calendar
    target_url = "https://www.nestle.com/investors/results"
    
    # Fetch the webpage content
    html_content = fetch_webpage_with_cookies(target_url)
    
    if not html_content:
        print("Failed to retrieve events calendar")
        return []
    
    # Parse events calendar
    events = parse_events_calendar(html_content)
    
    # Enrich events with data files
    enriched_events = []
    for event in events:
        # Extract data files for each event
        event['data'] = extract_data_files(event['href'])
        
        # Only add events with data files
        if event['data']:
            enriched_events.append(event)
            print(enriched_events)
    
    # Save to JSON
    output_file = "nesn_finance.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_events, f, indent=2, ensure_ascii=False)
    
    print(f"Total events processed: {len(enriched_events)}")
    print(f"Events saved to {output_file}")
    
    return enriched_events

if __name__ == '__main__':
    press_release_scraper()
    comprehensive_nestle_event_scraper()
    # events = []