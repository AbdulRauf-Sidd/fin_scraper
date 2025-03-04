import re
from dateutil.parser import parse
from datetime import datetime


def classify_frequency(event_name, event_url):
    # Define a regex pattern that matches the keywords indicating a periodic event
    periodic_keywords = r'\b(annual|quarterly|quarter|Q[1234]|full year|full_year|fullyear|)\b'
    
    # Check if the keywords are in the event name or file name
    if re.search(periodic_keywords, event_name, re.IGNORECASE) or re.search(periodic_keywords, event_url, re.IGNORECASE):
        return "periodic"
    else:
        return "non-periodic"   


def classify_periodic_type(event_name, event_url):
    # Define regex patterns to detect 'annual' and 'quarterly' anywhere in the strings
    annual_keywords = r'annual'
    quarterly_keywords = r'(quarterly|quarter|Q[1234])'
    
    # Check for 'annual' keyword in the event name or URL
    if re.search(annual_keywords, event_name, re.IGNORECASE) or \
       re.search(annual_keywords, event_url, re.IGNORECASE):
        return "annual"
    
    # Check for 'quarterly' keywords in the event name or URL
    elif re.search(quarterly_keywords, event_name, re.IGNORECASE) or \
         re.search(quarterly_keywords, event_url, re.IGNORECASE):
        return "quarterly"
    
    # Fallback or default condition if no keywords found
    else:
        return 'quarterly'  # or another handling mechanism as required
    
import re

def classify_euro_periodic_type(event_name, event_url):
    """
    Classifies an event as 'half-year', 'nine-month', '3-month', or 'annual' 
    based on the event name or URL.
    """
    # Define regex patterns for classification
    annual_keywords = r'\b(annual|full year|FY|fiscal year)\b'
    half_year_keywords = r'\b(half[-\s]?year|HY|6[-\s]?month|six[-\s]?month)\b'
    nine_month_keywords = r'\b(nine[-\s]?month|9[-\s]?month|third[-\s]?quarter)\b'
    three_month_keywords = r'\b(first[-\s]?quarter|second[-\s]?quarter|fourth[-\s]?quarter|Q[1234]|3[-\s]?month)\b'

    # Check for 'annual' keywords first
    if re.search(annual_keywords, event_name, re.IGNORECASE) or \
       re.search(annual_keywords, event_url, re.IGNORECASE):
        return "annual"
    
    # Check for 'half-year' keywords
    if re.search(half_year_keywords, event_name, re.IGNORECASE) or \
       re.search(half_year_keywords, event_url, re.IGNORECASE):
        return "half-year"
    
    # Check for 'nine-month' keywords
    if re.search(nine_month_keywords, event_name, re.IGNORECASE) or \
       re.search(nine_month_keywords, event_url, re.IGNORECASE):
        return "nine-month"
    
    # Check for '3-month' keywords
    if re.search(three_month_keywords, event_name, re.IGNORECASE) or \
       re.search(three_month_keywords, event_url, re.IGNORECASE):
        return "3-month"

    # Default to '3-month' if no specific pattern is found
    return "3-month"




def format_quarter_string(event_date, event_name):
    try:
        # Attempt to parse the event date considering common date formats including those with month abbreviations
        parsed_date = parse(event_date, fuzzy=True)
        # Determine the quarter from the parsed date
        quarter = (parsed_date.month - 1) // 3 + 1
        quarter_year_str = f"Q{quarter} {parsed_date.year}"
    except (ValueError, TypeError):
        # If date parsing fails, attempt to extract quarter from the event name
        quarter_year_str = extract_quarter_from_name(event_name)
        if not quarter_year_str:
            # If no quarter info is found, try to extract just the year
            year_match = re.search(r'(\b\d{4}\b)', event_name)
            year = year_match.group(0) if year_match else "Unknown Year"
            quarter_year_str = f"Year {year}"

    return quarter_year_str

def extract_quarter_from_name(event_name):
    # Regular expressions to identify quarter and year from the event name
    quarter_patterns = [
         r'Q([1-4]).*(\d{4})',  # Loosely matches 'Q1 2020' and similar, with any amount of whitespace between
        r'(\d{4}).*Q([1-4])',  # Matches '2020 Q1' and similar, with any amount of whitespace between
        r'(first|second|third|fourth)\s+quarter.*?(\d{4})',  # Matches 'first quarter ... 2020'
        r'(\d{4}).*?(first|second|third|fourth)\s+quarter'  # Matches '2020 ... first quarter'
        r'(\bJan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?) \d{4}\b'  # Matches month names and abbreviations followed by a year
    ]
    for pattern in quarter_patterns:
        match = re.search(pattern, event_name, re.IGNORECASE)
        if match:
            # Handle numeric and named quarters
            quarter_map = {'first': '1', 'second': '2', 'third': '3', 'fourth': '4', 'Jan': '1', 'Feb': '1', 'Mar': '1', 'Apr': '2', 'May': '2', 'Jun': '2', 'Jul': '3', 'Aug': '3', 'Sep': '3', 'Oct': '4', 'Nov': '4', 'Dec': '4'}
            quarter = match.group(1)
            if quarter.lower() in quarter_map:
                quarter = quarter_map[quarter.lower()]
            year = match.group(2) if len(match.groups()) > 1 else match.group(0).split()[-1]
            return f"Q{quarter} {year}"

    return None

def extract_euro_event_name(event_date, event_name):
    """
    Extract financial reporting period from event date or name.
    
    Supports extraction of:
    - Fiscal Year (FY YYYY)
    - Half-Year (H1 YYYY or H2 YYYY)
    - Nine-Month Results (9M YYYY)
    - Three-Month Results (3M YYYY)
    
    Args:
        event_date (str): Date of the event
        event_name (str): Name of the event
    
    Returns:
        str or None: Formatted financial period or None if no match found
    """
    # Comprehensive list of patterns to match various financial period formats
    financial_patterns = [
        # Fiscal Year Patterns
        r'\b(FY|Fiscal Year)\s*(\d{4})\b',  # "FY 2023", "Fiscal Year 2023"
        
        # Half-Year Patterns
        r'\b(H[12])\s*(\d{4})\b',  # "H1 2023", "H2 2023"
        r'\b(First|Second)\s*Half\s*(\d{4})\b',  # "First Half 2023", "Second Half 2023"
        r'\b(Half-Year)\s*(?:Results)?\s*(\d{4})\b',  # "Half-Year Results 2023"
        
        # Nine-Month Patterns
        r'\b(9M|Nine\s*(?:[-\s]?Months?|Mo))\s*(\d{4})\b',  # "9M 2023", "Nine Months 2023", "Nine-Months 2023"
        r'\b(Nine\s*Months?)\s*(?:Results)?\s*(\d{4})\b',  # "Nine Months Results 2023"
        
        # Three-Month Patterns
        r'\b(3M|Three\s*(?:[-\s]?Months?|Mo))\s*(\d{4})\b',  # "3M 2023", "Three Months 2023"
        r'\b(Three\s*Months?)\s*(?:Results)?\s*(\d{4})\b',  # "Three Months Results 2023"
        
        # Additional variations with different word orders and spacing
        r'\b(\d{4})\s*(FY|H[12]|9M|3M)\b',  # "2023 FY", "2023 H1"
    ]
    
    # Try parsing from event date first
    try:
        parsed_date = parse(event_date, fuzzy=True)
        # Determine fiscal year and half-year based on parsed date
        fiscal_year = parsed_date.year
        month = parsed_date.month
        
        # Fiscal year typically starts in different months based on company (e.g., October, January)
        # Here we'll use a standard January start for fiscal year
        if month >= 1 and month <= 6:
            return f"H1 {fiscal_year}"
        elif month >= 7 and month <= 12:
            return f"H2 {fiscal_year}"
    except (ValueError, TypeError):
        pass
    
    # Try matching patterns in event name
    for pattern in financial_patterns:
        matches = re.findall(pattern, event_name, re.IGNORECASE)
        for match in matches:
            # Handle different match group orders
            if len(match) == 2:
                period, year = match
            else:
                year, period = match
            
            # Normalize period
            period = period.upper().replace(' ', '')
            
            # Map variations to standard formats
            period_map = {
                'FISCALYEAR': f'FY {year}',
                'FY': f'FY {year}',
                'FIRSTHALF': f'H1 {year}',
                'H1': f'H1 {year}',
                'SECONDHALF': f'H2 {year}',
                'H2': f'H2 {year}',
                'NINEMONTHS': f'9M {year}',
                '9M': f'9M {year}',
                'THREEMONTHS': f'3M {year}',
                '3M': f'3M {year}'
            }
            
            # Return the first matching format
            if period in period_map:
                return period_map[period]
    
    return None


async def parse_date(date_str):
    """Parse various date formats and return a standardized date."""
    date_str = date_str.strip()
    formats = ["%m/%d/%y", "%b %d, %Y", "%Y-%m-%d"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    print(f"⚠️ Error parsing date: {date_str}")
    return None

async def parse_date2(date_str):
    """Parse various datetime formats to return only the date in a standardized format."""
    date_str = date_str.strip().split('T')[0]  # Split to remove time part and get only the date
    formats = ["%Y-%m-%d", "%m/%d/%y", "%b %d, %Y"]  # Include ISO format first as it's most likely

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date  # Return formatted date
        except ValueError:
            continue

    print(f"⚠️ Error parsing date: {date_str}")
    return None

async def parse_date3(date_str):
    """Parses a date string like 'Tuesday, February 25, 2025' into 'YYYY/MM/DD' format."""
    try:
        parsed_date = parse(date_str, fuzzy=True)
        return parsed_date  # Returns a datetime object
    except Exception as e:
        print(f"⚠️ Error parsing date: {date_str} -> {e}")
        return None  # Return None if parsing fails

from urllib.parse import urlparse
import os

async def extract_file_name(file_url):
    """Extracts the file name from a given URL."""
    parsed_url = urlparse(file_url)
    return os.path.basename(parsed_url.path)

import re
from datetime import datetime

async def extract_date_from_filename(filename):
    """
    Extracts a date from a given file name, handling multiple date formats.
    
    Supported formats include:
    - YYYY-MM-DD, YYYY_MM_DD, YYYY.MM.DD
    - DD-MM-YYYY, DD_MM_YYYY, DD.MM.YYYY
    - Month DD, YYYY (e.g., March 15, 2024)
    - YYYYQ1, YYYY-Q1 (Quarterly formats)
    - FY YYYY (Fiscal Year formats)
    
    Returns:
        Extracted date as a string in YYYY-MM-DD format, or None if no date is found.
    """

    # List of regex patterns to match different date formats
    date_patterns = [
        r'(\d{4})[-_.](\d{1,2})[-_.](\d{1,2})',       # YYYY-MM-DD, YYYY_MM_DD, YYYY.MM.DD
        r'(\d{1,2})[-_.](\d{1,2})[-_.](\d{4})',       # DD-MM-YYYY, DD_MM_YYYY, DD.MM.YYYY
        r'([A-Za-z]+)[\s_-]?(\d{1,2}),?\s?(\d{4})',   # Month DD, YYYY
        r'(\d{4})[-_]?Q([1-4])',                      # YYYYQ1, YYYY-Q1 (Quarterly formats)
        r'FY[_-\s]?(\d{4})'                           # FY YYYY (Fiscal Year formats)
    ]

    for pattern in date_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            try:
                if len(match.groups()) == 3:
                    # Convert matched groups into a date string
                    raw_date = "-".join(match.groups())
                    parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
                    return parsed_date.strftime("%Y-%m-%d")

                elif len(match.groups()) == 2 and "Q" in match.group(0):
                    # Handle quarterly format (e.g., "2024Q1")
                    year, quarter = match.groups()
                    month = {"1": "01", "2": "04", "3": "07", "4": "10"}[quarter]
                    return f"{year}-{month}-01"

                elif len(match.groups()) == 1 and "FY" in match.group(0):
                    # Handle Fiscal Year format (FY 2024 → assume Jan 1st)
                    year = match.groups()[0]
                    return f"{year}-01-01"

                else:
                    # Handle named months (March 15, 2024 → 2024-03-15)
                    month, day, year = match.groups()
                    parsed_date = datetime.strptime(f"{month} {day} {year}", "%B %d %Y")
                    return parsed_date.strftime("%Y-%m-%d")

            except ValueError:
                print('Error parsing date from file name')  # Skip to the next pattern if parsing fails

    return None  # Return None if no date is found


import re
from datetime import datetime

async def extract_date_from_text(text):
    """
    Extracts a date from a given text string that contains a date in various formats.
    Returns a datetime object if found, else returns None.
    """

    # Regular expression to match various date formats
    date_patterns = [
        r"(\d{1,2})\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{4})",  # 12 May 2022
        r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})",  # 12/05/2022 or 12-05-2022
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2}),\s(\d{4})",  # May 12, 2022
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # Format 1: "12 May 2022"
                if len(match.groups()) == 3 and match.group(2).isalpha():
                    day, month, year = match.groups()
                    return datetime.strptime(f"{day} {month} {year}", "%d %B %Y")
                
                # Format 2: "12/05/2022" or "12-05-2022"
                elif len(match.groups()) == 3 and match.group(2).isdigit():
                    day, month, year = match.groups()
                    return datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
                
                # Format 3: "May 12, 2022"
                elif len(match.groups()) == 3 and match.group(1).isalpha():
                    month, day, year = match.groups()
                    return datetime.strptime(f"{day} {month} {year}", "%d %B %Y")

            except ValueError:
                pass  # Skip if parsing fails

    return None  # Return None if no date is found


async def accept_cookies(page):
    """Accepts cookies if a consent banner appears."""
    try:
        cookie_button = await page.query_selector("button:has-text('Accept')")
        if cookie_button:
            await cookie_button.click()
            await asyncio.sleep(2)  # Wait to ensure banner disappears
            print("✅ Accepted cookies.")
    except Exception as e:
        print(f"⚠️ No cookie consent banner found or error clicking it: {e}")

import asyncio