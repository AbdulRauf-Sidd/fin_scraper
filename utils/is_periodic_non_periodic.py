import re
import logging
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup

# Setting up the logger
logging.basicConfig(filename="scraping.log", level=logging.DEBUG, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Exhaustive periodic patterns for matching
PERIODIC_PATTERNS = [
    r"\bquarterly\b",           # matches quarterly
    r"\bannual\b",              # matches annual
    r"\byearly\b",              # matches yearly
    r"\bsemi[-\s]?annual\b",    # semi-annual
    r"\bquarter[-\s]?report\b", # quarterly report
    r"\bfiling\b",              # common filing term
    r"\binterim\b",             # interim
    r"\bhalf[-\s]?year\b",      # half-year
    r"\bmonthly\b",             # monthly
    r"\byear[-\s]?end\b",       # year-end
    r"\bannual\b",  # annual
    r"\bpreliminary\b",  # preliminary
    r"\bquarter\b",  # quarter
    r"\bhalf[-_\s]?year\b",  # half-year
    r"\bfull[-_\s]?year\b",  # full-year
    r"\bfigures\b",  # figures
    r"\bsemi[-_\s]?annual\b",  # semi-annual
    r"\bmonthly\b",  # monthly
    r"\bq[1-4]\b",              # Q1, Q2, Q3, Q4
    r"\bfy\b",                  # FY (Fiscal Year)
    r"\b[369]m\b",              # 3M, 6M, 9M (Months)
    r"\bh1\b",                  # H1 (First Half)
    r"\bh2\b",                  # H2 (Second Half)
    r"\bfinancial[-\s]?year\b",  # financial year
    r"\bfiscal[-\s]?year\b",     # fiscal year
    r"\b3m\b",                   # 3 months
    r"\b9m\b",                   # 9 months
]

# Function to classify the event/document type
def is_periodic_non_periodic(html_element):
    event_name = None
    is_periodic = False

    # Parse the HTML element (this could be a part of the document you're scraping)
    soup = BeautifulSoup(html_element, 'html.parser')
    text_content = soup.get_text(strip=True).lower()  # Extract text and make lowercase for easy matching
    
    # Check the URL (href) if present in the element
    url = soup.find('a', href=True)
    if url and url['href']:
        text_content += " " + url['href'].lower()

    logger.info(f"Classifying event: {text_content[:100]}...")  # Log the beginning of the event name or content for clarity

    # Check for periodic patterns (in both text and URL)
    for pattern in PERIODIC_PATTERNS:
        if re.search(pattern, text_content, re.IGNORECASE):
            logger.info(f"Pattern match found for periodic: {pattern}")
            is_periodic = True
            break

    # If periodic is not found, classify as non-periodic
    if not is_periodic:
        logger.info("No periodic pattern matched. Classifying as Non-Periodic")
        return "Non-Periodic"
    
    # If periodic is found
    logger.info("Event classified as Periodic")
    return "Periodic"

# # Example calls to the function
# html_element_example_1 = """<div class="result-line"><p>Quarterly Earnings Report Q4 2024</p></div>"""
# event_type_1 = classify_event(html_element_example_1)
# logger.info(f"Final Classification: {event_type_1}")

# html_element_example_2 = """<div class="result-line"><p>March 27, 2025 Financial Year 2024 Downloads Press Release Corporate Report 2024</p></div>"""
# event_type_2 = classify_event(html_element_example_2)
# logger.info(f"Final Classification: {event_type_2}")
