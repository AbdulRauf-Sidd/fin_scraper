import logging
import spacy
from playwright.async_api import Page
import re
import os

# Set up logging
log_file = os.path.join(os.path.dirname(__file__), "../logs/is_bad_link.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load spaCy model
nlp = spacy.load("en_core_web_md")  

# Define error phrases for NLP analysis
error_phrases = [
    "page not found",
    "error 404",
    "not authorized",
    "access denied",
    "service unavailable",
    "internal server error",
    "bad gateway",
    "forbidden",
    "this site can’t be reached",
    "temporarily unavailable",
    "problem loading page",
    "connection timed out",
    "file not found",
    "resource not available",
    'presentation no longer available',
    'presentation not found',
]

def detect_error_message(text: str) -> bool:
    """
    Detects if the given text contains error messages using NLP and logs similarity scores.
    """
    doc = nlp(text.lower())
    similarity_threshold = 0.8  # Define a threshold for similarity

    for phrase in error_phrases:
        phrase_doc = nlp(phrase)  # Create a spaCy Doc for the error phrase
        similarity = doc.similarity(phrase_doc)  # Calculate similarity score

        logger.debug(f"Similarity between '{text[:50]}...' and '{phrase}': {similarity:.2f}")

        if similarity > similarity_threshold:
            logger.info(f"❌ URL contains an error (similarity score: {similarity:.2f})")
            return True
    return False


async def _get_page_content(page: Page) -> tuple[str, int, str]:
    """
    Gets the content, status code, and content type from a Playwright page.
    """
    # Prepare variables
    content = ""
    status = 0
    content_type = ""
    
    try:
        # Listen for response and capture the status code and content type
        response = await page.goto(page.url)  # Load the page
        status = response.status
        content_type = response.headers.get("content-type", "")
        content = await page.content()  # Get the page content
        
    except Exception as e:
        logger.error("❌ Error while getting page content for URL %s: %s", page.url, e)
        return "", 0, ""
    
    return content, status, content_type

async def is_bad_link(page: Page) -> bool:
    """
    Checks if a given page points to a broken or error page.
    Returns True if the page is determined to be a bad/broken page,
    False if the page appears valid.
    """
    url = page.url

    logger.info("════════════════════════════════════════════════════════════════════")
    logger.info("Checking page URL: %s", url)

    try:
        content, status_code, content_type = await _get_page_content(page)
        logger.debug("Received HTTP status code: %s", status_code)
    except Exception as e:
        logger.error("❌ Failed to get page content for URL %s: %s", url, e)
        logger.info("🔴 BAD LINK (request failed)\n")
        return True

    # Immediately mark as bad if a known error HTTP status is returned
    if status_code in [404, 410, 403, 500, 502, 503, 504]:
        logger.info("❌ URL %s returned error status code: %s", url, status_code)
        logger.info("🔴 BAD LINK (HTTP error)\n")
        return True

    logger.debug("Content-Type for URL %s: %s", url, content_type)

    if "text/html" in content_type.lower():
        try:
            # Take only first 2KB of content for analysis
            text_snippet = content[:2048]
            logger.debug("Fetched HTML content for NLP analysis.")
        except Exception as e:
            logger.error("❌ Error processing content from URL %s: %s", url, e)
            logger.info("🔴 BAD LINK (decode failure)\n")
            return True

        if detect_error_message(text_snippet):
            logger.info("❌ URL %s determined to be a bad link based on NLP analysis.", url)
            logger.info("🔴 BAD LINK (NLP detected error page)\n")
            return True
        else:
            logger.info("✅ NLP analysis passed. No error message found.")
    else:
        logger.debug("Non-HTML content detected (Content-Type: %s)", content_type)

        # Read a small portion of non-HTML content to detect XML error messages
        try:
            content = response.content[:2048]
            encoding = response.encoding if response.encoding else "utf-8"
            text_snippet = content.decode(encoding, errors="ignore").lower()

            # Check for common XML error patterns
            if "<error>" in text_snippet or "authorization" in text_snippet or "access denied" in text_snippet or "<code>" in text_snippet:
                logger.info("❌ Non-HTML content contains error-indicating XML or text.")
                logger.info("🔴 BAD LINK (XML or authorization error in non-HTML response)\n")
                return True

        except Exception as e:
            logger.error("Error while checking non-HTML content for error markers: %s", e)
            logger.info("🔴 BAD LINK (non-HTML decode failure)\n")
            return True

        logger.info("🟢 GOOD LINK\n")

    logger.info("🟢 GOOD LINK\n")
    return False

# ---------------------------------------------------------
# Example usage (for testing purposes):
# ---------------------------------------------------------
import asyncio
from playwright.async_api import async_playwright

async def main():
    test_urls = [
        "https://annualreport.dsm.com/ar2019/xmlpages/resources/TXP/dsm/ar_2019/files/DSM-Annual-Report-2019.pdf/",  # Expected to be good.
        "https://3c5636b6cfe0011ec1887ff62b057097.r2.cloudflarestorage.com/fin-scraping-bucket/KO/2025-02-20/board-of-directors-of-the-coca-cola-company-approves-63rd/board-of-directors-of-the-coca-cola-company-approves-63rd",
        "https://www.example.com/thispagedoesnotexist",  # Likely to return a 404 or error page.
        "https://www.croda.com/en-gb/sustainability/ethics",
        "https://archlabs.tech/"
    ]

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context()
        for url in test_urls:
            page = await context.new_page()
            try:
                await page.goto(url, timeout=60000)  # Set a timeout for navigation
                result = await is_bad_link(page)
                print(f"{url} is bad: {result}")
            except Exception as e:
                print(f"Error processing {url}: {e}")
            finally:
                await page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
