import re
from dateutil.parser import parse
from datetime import datetime


def classify_frequency(event_name, event_url):
    # Define a regex pattern that matches the keywords indicating a periodic event
    periodic_keywords = r'\b(annual|quarterly|quarter|Q[1234])\b'
    
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


from urllib.parse import urlparse
import os

def extract_file_name(file_url):
    """Extracts the file name from a given URL."""
    parsed_url = urlparse(file_url)
    return os.path.basename(parsed_url.path)