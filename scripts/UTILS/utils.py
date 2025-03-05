import re
from dateutil.parser import parse
from datetime import datetime
import json

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
            return event_name

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

    return "NULL"  # Return None if no date is found


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
import re

def categorize_event(event_name: str) -> str:
    """
    Categorizes a non-periodic event name based on predefined event types.

    :param event_name: The name of the event
    :return: The category of the event
    """

    # *Step 1: Direct Matching for Core Event Names*
    exact_matches = {
        r"\bpress\b|\bpress release\b": "press_release",
        r"\bcapital markets\b|\bcapital markets day\b": "capital_markets_day",
        r"\bannual general\b|\bannual meeting\b|\bagm\b": "annual_general_meeting",
        r"\bfact\b|\bfact sheet\b|\bfact book\b": "fact_sheet",
        r"\btrading\b|\bupdate\b|\btrading update\b": "trading_updates",
        r"\besg\b|\bsustainability\b|\bsustainability report\b": "esg",
        r"\banalyst\b|\banalyst presentation\b|\banalyst event\b": "analyst_presentations"
    }

    event_name_lower = event_name.lower().strip()

    for pattern, category in exact_matches.items():
        if re.search(pattern, event_name_lower, re.IGNORECASE):
            return category  # Return immediately if a direct match is found

    # *Step 2: Pattern Matching for More Variations*
    patterns = {
        "press_release": re.compile(
            r"(press|announce|approval|update|break ground|expansion|hire|transition|"
            r"contract option|convertible notes|prices upsized|proposed senior notes|"
            r"board changes|collaborates with|strategic partnership|merger|acquisition|"
            r"regulatory approval|business update|new product launch|earnings release)", 
            re.IGNORECASE
        ),
        "capital_markets_day": re.compile(
            r"(capital markets|investor day|analyst day|seminar|conference|fireside chat|"
            r"site visit|industry event|roadshow|investor presentation)", 
            re.IGNORECASE
        ),
        "annual_general_meeting": re.compile(
            r"(annual report|notification to shareholders|proxy|shareholder meeting|agm)", 
            re.IGNORECASE
        ),
        "fact_sheet": re.compile(
            r"(fact sheet|fact book|infographic|ratings and frameworks|awards|certifications|"
            r"policies|procedures|ethics|summary report|key figures|performance highlights)", 
            re.IGNORECASE
        ),
        "trading_updates": re.compile(
            r"(trading update|full[\s\-]?year results|quarterly results|earnings call|"
            r"financial highlights|business performance|quarterly earnings|interim report|"
            r"half-year results|FY\d{2})",  # Matches things like "FY23"
            re.IGNORECASE
        ),
        "esg": re.compile(
            r"(sustainability report|sustainability strategy|carbon footprint|"
            r"environmental impact|climate change|diversity and inclusion|social impact|"
            r"corporate responsibility)", 
            re.IGNORECASE
        ),
        "analyst_presentations": re.compile(
            r"(analyst presentation|analyst event|fireside chat|banking conference|investor call|"
            r"sell-side meeting|earnings call|broker conference)", 
            re.IGNORECASE
        ),
        "other": re.compile(
            r"(prospectus|notification filed|registration of securities|"
            r"regulatory filing|ownership disclosure|securities update|legal filing)", 
            re.IGNORECASE
        ),
    }

    # *Step 3: Apply Pattern Matching*
    for category, regex in patterns.items():
        if regex.search(event_name_lower):
            return category

    # *Step 4: Fallback Categorization*
    if "presentation" in event_name_lower:
        return "fact_sheet"
    if "meeting" in event_name_lower:
        return "annual_general_meeting"
    if "results" in event_name_lower or "update" in event_name_lower:
        return "trading_updates"
    
    return "other"  # Default if no match is found

def save_json(data, filename):
    file_mode = 'a' if os.path.exists(filename) else 'w'
    with open(filename, file_mode) as f:
        if file_mode == 'a':  # File exists, append to it
            f.seek(0, os.SEEK_END)  # Seek to end of file
            f.seek(f.tell() - 1, os.SEEK_SET)  # Go back one character from the end
            f.truncate()  # Remove the last character (should be a closing bracket ])
            f.write(',\n')  # Prepare for new JSON object
            json.dump(data, f)
            f.write(']')
        else:  # File does not exist, create new
            json.dump([data], f)  # Write data as a list of JSON objects


def classify_document(event_name: str, url: str) -> str:
    """
    Classifies the document type based on the event name and URL.
    
    Possible categories:
    - presentation
    - report
    - transcript
    - financial statements
    - news
    - spreadsheet
    - other
    """

    event_name = event_name.lower()
    url = url.lower()

    patterns = {
        "presentation": [
            r"presentation", r"slide\s*deck", r"slideshow", r"investor\s*day", r"earnings\s*deck"
        ],
        "report": [
            r"annual\s*report", r"quarterly\s*report", r"10-?k", r"10-?q", r"financial\s*report",
            r"earnings\s*report", r"sec\s*filing", r"disclosure", r"statement", r"report\b"
        ],
        "transcript": [
            r"transcript", r"earnings\s*call", r"conference\s*call", r"call\s*notes"
        ],
        "financial statements": [
            r"balance\s*sheet", r"cash\s*flow", r"income\s*statement", r"financial\s*statement",
            r"statement\s*of\s*operations"
        ],
        "news": [
            r"press\s*release", r"announcement", r"news", r"disclosure", r"media\s*statement"
        ],
        "spreadsheet": [
            r"\.xlsx", r"\.xls", r"excel", r"spreadsheet", r"csv"
        ]
    }

    for category, regex_list in patterns.items():
        for pattern in regex_list:
            if re.search(pattern, event_name) or re.search(pattern, url):
                return category

    return "other"


def get_file_type(url: str) -> str:
    """
    Extracts the file type from a URL.
    
    Recognized types:
    - pdf
    - csv
    - xlsx
    - mp4
    - etv
    - html (default)
    """

    url = url.lower()

    file_patterns = {
        "pdf": r"\.pdf(\?|$)",
        "csv": r"\.csv(\?|$)",
        "xlsx": r"\.xlsx(\?|$)|\.xls(\?|$)",  # Covers .xls and .xlsx
        "mp4": r"\.mp4(\?|$)",
        "etv": r"\.etv(\?|$)"
    }

    for file_type, pattern in file_patterns.items():
        if re.search(pattern, url):
            return file_type

    return "html"