import re
import logging
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup

# Setting up the logger
logging.basicConfig(filename="logs/is_periodic_non_periodic.log", level=logging.DEBUG, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Regular expressions for detecting common periodic vs non-periodic patterns
PERIODIC_PATTERNS = [
    r"\bquarterly\b",  # matches quarterly
    r"\bannual\b",     # matches annual
    r"\byearly\b",     # matches yearly
    r"\bsemi[-\s]?annual\b",  # semi-annual
    r"\bquarter[-\s]?report\b", # quarterly report
    r"\bfiling\b", # common filing term
    r"\b10[-\s]?k\b",  # matches 10-k
    r"\b10[-\s]?q\b",  # matches 10-q
    r"\bq[1-4]\b",  # matches Q1, Q2, Q3, Q4
    r"\bfy\b",  # matches FY (Fiscal Year)
    r"\bh[1-2]\b",  # matches H1, H2 (Half Year)
    r"\bhalf[-\s]?year\b",  # matches half-year
    r"\bnine[-\s]?month\b",  # matches nine-month
    r"\b3[-\s]?month\b",  # matches 3-month
    r"\b9[-\s]?month\b",  # matches 9-month
    r"\bfull[-\s]?year\b",  # matches full-year
    r"\bannual[-\s]?report\b",  # matches annual report
    r"\binterim[-\s]?report\b",  # matches interim report
    r"\bsemi[-\s]?annual[-\s]?report\b",  # matches semi-annual report
    r"\bquarter[-\s]?results\b",  # matches quarter results
    r"\bhalf[-\s]?year[-\s]?results\b",  # matches half-year results
    r"\bannual[-\s]?results\b",  # matches annual results
    r"\bpreliminary[-\s]?results\b",  # matches preliminary results
    r"\bfiscal[-\s]?year\b",  # matches fiscal year
    r"\binterim\b",  # matches interim

]

NON_PERIODIC_PATTERNS = [
    r"\bpress[-\s]?release\b",  # press release
    r"\bwebcast\b",              # webcast
    r"\bconference[-\s]?call\b",  # conference call
    r"\b8[-\s]?k\b",  # matches 8-k
    r"\bschedule[-\s]?13d\b",  # matches schedule 13d
    r"\bschedule[-\s]?13g\b",  # matches schedule 13g
    r"\bform[-\s]?3\b",  # matches form 3
    r"\bform[-\s]?4\b",  # matches form 4
    r"\bform[-\s]?5\b",  # matches form 5
    r"\bform[-\s]?sd\b",  # matches form sd
    r"\bform[-\s]?8[-\s]?a\b",  # matches form 8-a
    r"\bform[-\s]?s[-\s]?1\b",  # matches form s-1
    r"\bform[-\s]?s[-\s]?3\b",  # matches form s-3
    r"\bform[-\s]?s[-\s]?4\b",  # matches form s-4
    r"\bform[-\s]?f[-\s]?1\b",  # matches form f-1
    r"\bform[-\s]?f[-\s]?3\b",  # matches form f-3
    r"\bform[-\s]?f[-\s]?4\b",  # matches form f-4
    r"\bform[-\s]?d\b",  # matches form d
    r"\bform[-\s]?144\b",  # matches form 144
]

# Function to classify the event/document type
def is_periodic_non_periodic(html_element, geography):
    event_name = None
    is_periodic = False
    is_non_periodic = False

    # Parse the HTML element (this could be a part of the document you're scraping)
    soup = BeautifulSoup(html_element, 'html.parser')
    text_content = soup.get_text(strip=True).lower()  # Extract text and make lowercase for easy matching

    # Check patterns based on the geography (US or European)
    logger.info(f"Classifying event with geography: {geography}")

    # US or European-based keyword detection
    if geography.lower() == 'us':
        logger.info("Geography set to US")
        # Check for periodic patterns
        for pattern in PERIODIC_PATTERNS:
            if re.search(pattern, text_content, re.IGNORECASE):
                logger.info(f"Pattern match found for periodic: {pattern}")
                is_periodic = True
                break

        # Check for non-periodic patterns
        for pattern in NON_PERIODIC_PATTERNS:
            if re.search(pattern, text_content, re.IGNORECASE):
                logger.info(f"Pattern match found for non-periodic: {pattern}")
                is_non_periodic = True
                break

    elif geography.lower() == 'european':
        logger.info("Geography set to European")
        # Adjust your patterns or add other rules specific for European standards
        # For example, you might encounter more non-periodic webcasts or calls in some regions
        # Check European periodic patterns (if different from US)
        # Here, add more European-specific pattern checks if needed

        # Similar checks to US or specific European tweaks
        for pattern in PERIODIC_PATTERNS:
            if re.search(pattern, text_content, re.IGNORECASE):
                logger.info(f"Pattern match found for periodic (European): {pattern}")
                is_periodic = True
                break

        for pattern in NON_PERIODIC_PATTERNS:
            if re.search(pattern, text_content, re.IGNORECASE):
                logger.info(f"Pattern match found for non-periodic (European): {pattern}")
                is_non_periodic = True
                break

    else:
        logger.error(f"Invalid geography input: {geography}")
        return None

    # If both periodic and non-periodic were flagged, use NLP-based similarity to decide
    if is_periodic and is_non_periodic:
        logger.info("Both periodic and non-periodic patterns matched, using NLP-based similarity matching.")
        # Example similarity score between periodic and non-periodic categories
        score = fuzz.ratio(text_content, "quarterly report")  # Adjust based on similarity score
        if score > 80:
            logger.info(f"Text closely matches periodic event with a similarity score of {score}")
            return "Periodic"
        else:
            logger.info(f"Text closely matches non-periodic event with a similarity score of {score}")
            return "Non-Periodic"

    if is_periodic:
        logger.info("Event classified as Periodic")
        return "Periodic"
    elif is_non_periodic:
        logger.info("Event classified as Non-Periodic")
        return "Non-Periodic"
    else:
        logger.info("No classification match found.")
        return "Unclassified"

# # Example call to the function
# html_element_example = """<div class="result-line"><p>Quarterly Earnings Report Q4 2024</p></div>"""
# event_type = is_periodic_non_periodic("annual report", "US")
# logger.info(f"Final Classification: {event_type}")

# Example of periodic and non-periodic cases
