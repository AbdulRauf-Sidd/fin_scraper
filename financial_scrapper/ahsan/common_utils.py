import re
import json
import os
from urllib.parse import urljoin

import re
from datetime import datetime

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

async def extract_date_from_text(text):
    """
    Extracts a date from a given text string that contains a date in various formats.
    Returns a datetime object if found, else returns "NULL".
    """

    # Regular expression to match various date formats
    date_patterns = [
        r"(\d{1,2})\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{4})",  # 12 May 2022
        r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})",  # 12/05/2022 or 12-05-2022
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2}),\s(\d{4})",  # May 12, 2022
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            # Depending on the date format, extract and convert to a datetime object
            try:
                if len(match.groups()) == 3:  # For formats like "12 May 2022" or "May 12, 2022"
                    date_str = f"{match.group(2)} {match.group(1)}, {match.group(3)}"  # e.g., "May 12, 2022"
                    return str(datetime.strptime(date_str, "%B %d, %Y"))
                elif len(match.groups()) == 3:  # For formats like "12/05/2022"
                    date_str = f"{match.group(3)}-{match.group(1)}-{match.group(2)}"  # e.g., "2022-12-05"
                    return str(datetime.strptime(date_str, "%Y-%m-%d"))
            except ValueError:
                continue  # Skip invalid date format and move to next pattern

    return "NULL"


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

def classify_frequency(event_name, file_name):
    # Define a regex pattern that matches the keywords indicating a periodic event
    periodic_keywords = r'\b(annual|quarterly|quarter|Q[1234])\b'
    
    # Check if the keywords are in the event name or file name
    if re.search(periodic_keywords, event_name, re.IGNORECASE) or re.search(periodic_keywords, file_name, re.IGNORECASE):
        return "periodic"
    else:
        return "non-periodic"
    
def ensure_absolute_url(base_url, url):
    from urllib.parse import urljoin

    # Check if the URL is already absolute
    if url.startswith('http'):
        return url
    else:
        # Combine the base URL with the relative URL to create an absolute URL
        return urljoin(base_url, url)

async def KO_close_cookie_consent(page):
    # Check if the cookie consent form is visible
    cookie_consent_selector = "#onetrust-pc-sdk"
    close_button_selector = "#close-pc-btn-handler"
    try:
        # Wait for the cookie consent form to appear (up to 5 seconds)
        cookie_consent = await page.wait_for_selector(cookie_consent_selector, state="attached", timeout=5000)
        if cookie_consent:
            print("Cookie consent form found. Attempting to close...")
            await page.click(close_button_selector)
            print("Cookie consent form closed.")
        else:
            print("No cookie consent form found.")
    except Exception as e:
        print(f"No cookie consent form to close or an error occurred: {str(e)}")