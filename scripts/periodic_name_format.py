import re
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

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

# Example Usage
event_date = ""
event_name = "Q3 financial results 2025"
formatted_name = format_quarter_string(event_date, event_name)
print(formatted_name)  # Output: "Q3 2025"
