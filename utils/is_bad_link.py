import requests
import logging
import spacy

# ---------------------------------------------------------
# Set up logging: detailed logs written to bad_link_check.logs
# ---------------------------------------------------------
logger = logging.getLogger("BadLinkChecker")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# File handler writes detailed logs to file
file_handler = logging.FileHandler("logs/is_bad_link.logs")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# # Optionally, add a stream handler for console output (can be removed in production)
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.INFO)
# stream_handler.setFormatter(formatter)
# logger.addHandler(stream_handler)

# ---------------------------------------------------------
# Load the spaCy model for NLP analysis
# We try to load a model with word vectors (en_core_web_md) for better similarity scores.
# ---------------------------------------------------------
try:
    nlp = spacy.load("en_core_web_md")
    logger.info("Loaded spaCy model 'en_core_web_md'.")
    logger.info("\n")  # This will insert a blank line in the log

except Exception as e:
    logger.error("Error loading 'en_core_web_md': %s. Falling back to 'en_core_web_sm'.", e)
    logger.info("\n")  # This will insert a blank line in the log
    nlp = spacy.load("en_core_web_sm")

# ---------------------------------------------------------
# Pre-define a list of error message prototypes.
# These phrases capture common patterns in error pages.
# ---------------------------------------------------------
error_phrases = [
    "404",
    "not found",
    "page not found",
    "error 404",
    "server error",
    "page no longer exists",
    "cannot be found",
    "page is missing",
    "error occurred",
    "page not available",
    "temporarily unavailable",
    "access denied",
    "forbidden",
    "bad request",
    "internal server error",
    "the page you requested could not be found",
    "the requested url was not found on this server",
    "oops, something went wrong",
    "page removed",
    "access denied",
    "signature does not match",
    "missing required headers",
    "authentication failed",
    "bucket not found",
    "object does not exist"
]

import re

def _sanitize_url(url: str) -> str:
    """
    Cleans a URL string by stripping quotes, backslashes, commas, and whitespace.
    Useful for malformed input like '\"https://example.com\\",' etc.
    """
    return re.sub(r'[\\\'",]+$', '', url.strip().strip('"\''))


# Pre-compute spaCy docs for each error phrase for later similarity comparisons.
error_docs = [nlp(phrase) for phrase in error_phrases]

# ---------------------------------------------------------
# Define a function that uses NLP to check if a text snippet
# contains any error-message-like content.
# ---------------------------------------------------------
def detect_error_message(text: str, threshold: float = 0.92) -> bool:
    """
    Analyzes the text using NLP to determine if it contains indicators
    of an error page. Returns True if any sentence in the text is
    similar to a known error phrase above the similarity threshold.
    """
    logger.debug("Starting NLP analysis on text snippet.")
    doc = nlp(text)

    for sent in doc.sents:
        sent_text = sent.text.strip().lower()
        preview = sent_text[:100].replace("\n", " ").strip() + ("..." if len(sent_text) > 100 else "")
        logger.debug("Analyzing sentence preview: '%s'", preview)

        for error_doc in error_docs:
            similarity = sent.similarity(error_doc)
            logger.debug("Similarity to error phrase '%s': %.2f", error_doc.text, similarity)

            if similarity >= threshold:
                logger.info("Detected error message in sentence (preview): '%s' (similarity: %.2f)", preview, similarity)
                return True

    logger.debug("No error message detected in the analyzed text snippet.")
    return False

# ---------------------------------------------------------
# Main function: is_bad_link
# It accesses the URL, checks the HTTP status code, and if HTML is returned,
# it only downloads a small snippet of content to run the NLP analysis.
# ---------------------------------------------------------
async def is_bad_link(url: str) -> bool:
    """
    Checks if a given URL points to a broken or error page.
    Returns True if the link is determined to be a bad/broken link,
    False if the link appears valid.
    """
    url = _sanitize_url(url)

    logger.info("════════════════════════════════════════════════════════════════════")
    logger.info("Checking URL: %s", url)

    try:
        # Use stream=True to avoid downloading the full content unnecessarily.
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10, stream=True)

        logger.debug("Received HTTP status code: %s", response.status_code)
    except requests.exceptions.RequestException as e:
        logger.error("❌ Request failed for URL %s: %s", url, e)
        logger.info("🔴 BAD LINK (request failed)\n")
        return True

    # Immediately mark as bad if a known error HTTP status is returned.
    if response.status_code in [404, 410, 403, 500, 502, 503, 504]:
        logger.info("❌ URL %s returned error status code: %s", url, response.status_code)
        logger.info("🔴 BAD LINK (HTTP error)\n")
        return True

    content_type = response.headers.get("Content-Type", "")
    logger.debug("Content-Type for URL %s: %s", url, content_type)

    if "text/html" in content_type:
        try:
            # Read only the first 2 KB to limit processing time.
            content = response.content[:2048]
            encoding = response.encoding if response.encoding else "utf-8"
            text_snippet = content.decode(encoding, errors="ignore")
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
if __name__ == "__main__":
    test_urls = [
        "https://annualreport.dsm.com/ar2019/xmlpages/resources/TXP/dsm/ar_2019/files/DSM-Annual-Report-2019.pdf/",             # Expected to be good.
        "https://3c5636b6cfe0011ec1887ff62b057097.r2.cloudflarestorage.com/fin-scraping-bucket/KO/2025-02-20/board-of-directors-of-the-coca-cola-company-approves-63rd/board-of-directors-of-the-coca-cola-company-approves-63rd",
        "https://www.example.com/thispagedoesnotexist",  # Likely to return a 404 or error page.
        "https://www.croda.com/en-gb/sustainability/ethics",
    ]
    
    for url in test_urls:
        result =  is_bad_link(url)
        print(f"{url} is bad: {result}")
