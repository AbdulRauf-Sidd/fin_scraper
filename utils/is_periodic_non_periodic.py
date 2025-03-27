import re
import logging
from bs4 import BeautifulSoup

# Setting up the logger
logging.basicConfig(filename="logs/is_periodic_non_periodic.log", level=logging.DEBUG, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Exhaustive periodic patterns for matching
PERIODIC_PATTERNS = [
    r"\bquarterly\b",                     # matches quarterly
    r"\bannual\b",                        # matches annual
    r"\byearly\b",                        # matches yearly
    r"\bsemi[-_\s]?annual\b",             # semi-annual
    r"\bquarter[-_\s]?report\b",          # quarterly report
    r"\bfiling\b",                        # common filing term
    r"\binterim\b",                       # interim
    r"\bhalf[-_\s]?year\b",               # half-year
    r"\bmonthly\b",                       # monthly
    r"\byear[-_\s]?end\b",                # year-end
    r"\bpreliminary\b",                   # preliminary
    r"\bquarter\b",                       # quarter
    r"\bfull[-_\s]?year\b",               # full-year
    r"\bfigures\b",                       # figures
    r"\bq[1-4]\b",                        # Q1, Q2, Q3, Q4
    r"\bfy\b",                            # FY (Fiscal Year)
    r"\b[369]m\b",                        # 3M, 6M, 9M (Months)
    r"\bh[12]\b",                         # H1 (First Half), H2 (Second Half)
    r"\bfinancial[-_\s]?year\b",          # financial year
    r"\bfiscal[-_\s]?year\b",             # fiscal year
    r"\b[369][-_\s]?months?\b",           # 3 months, 6 months, 9 months
    r"\bannual[-_\s]?report\b",           # annual report
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",  # months
    r"\b(january[-_\s]?to[-_\s]?september|january[-_\s]?september)\b",  # date ranges like January-September
    r"\b\d{1,2}[-_\s]?(january|february|march|april|may|june|july|august|september|october|november|december)[-_]?\d{4}\b",  # specific dates like March 01, 2022
]

# Function to classify the event/document type
def is_periodic_non_periodic(html_element):
    event_name = None
    is_periodic = False

    # Parse the HTML element (this could be a part of the document you're scraping)
    soup = BeautifulSoup(html_element, 'html.parser')
    text_content = soup.get_text(strip=True).lower()  # Extract text and make lowercase for easy matching
    
    # Clean the text content to handle extra spaces, hidden characters, etc.
    text_content = re.sub(r'\s+', ' ', text_content)  # Replace multiple spaces with a single space

    # Check the URL (href) if present in the element
    url = soup.find('a', href=True)
    if url and url['href']:
        url_content = url['href'].lower()
        url_content = re.sub(r'\s+', ' ', url_content)  # Clean the URL content as well
        text_content += " " + url_content

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
# event_type_1 = is_periodic_non_periodic(html_element_example_1)
# logger.info(f"Final Classification: {event_type_1}")

# html_element_example_2 = """<div class="result-line"><p>March 27, 2025 Financial Year 2024 Downloads Press Release Corporate Report 2024</p></div>"""
# event_type_2 = is_periodic_non_periodic(html_element_example_2)
# logger.info(f"Final Classification: {event_type_2}")