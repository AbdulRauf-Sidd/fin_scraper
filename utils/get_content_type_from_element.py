import re
import logging
import math
import spacy
from bs4 import BeautifulSoup
from typing import List, Union

# -------------------------
# Logging and spaCy setup
# -------------------------
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Load a spaCy model; adjust as needed for your environment.
nlp = spacy.load("en_core_web_sm")

# -------------------------
# Utility: Cosine Similarity
# -------------------------
def _cosine_similarity(vec_a, vec_b):
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for a, b in zip(vec_a, vec_b):
        dot += a * b
        norm_a += a * a
        norm_b += b * b
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))

# -------------------------
# Content Type Patterns & Concepts
# -------------------------
CONTENT_PATTERNS = {
    r"\b10[-_\s]?k\b": ["10-K", "sec-filing"],
    r"\b10[-_\s]?q\b": ["10-Q", "sec-filing"],
    r"\bannual[-_\s]+report\b": ["annual-report"],
    r"\bsec[-_\s]+filings?\b": ["sec-filing"],
    r"\bfinancials?\b": ["financial-filing"],
    r"\breports?\b": ["financial-filing"],
    r"\bearnings[-_\s]+release\b": ["financial-filing"],
    r"\bpress[-_\s]+release\b": ["press-release"],
    r"\bpresentation\b": ["presentation"],
    r"\btranscript\b": ["transcript"],
    r"\bwebcast\b": ["webcast"],
    r"\bspreadsheet\b": ["spreadsheet"],
    r"\bsellside[-_\s]+conference\b": ["sellside-conference"],
    r"\bindustry[-_\s]+conference\b": ["industry-conference"],
    r"\binvestor[-_\s]+day[-_\s]+presentation\b": ["investor-day-presentation"],
    r"\bpreliminary[-_\s]+results?\b": ["preliminary-results"],
    r"\binterim[-_\s]+results?\b": ["interim-results"],
    r"\btrading[-_\s]+update\b": ["trading-update"],
    r"\bfull[-_\s]?year[-_\s]+results?\b": ["full-year-results"],
    r"\bnine[-_\s]?month[-_\s]+sales?\b": ["nine-month-sales"],
    r"\bhalf[-_\s]?year[-_\s]+results?\b": ["half-year-results"],
    r"\bthree[-_\s]?month[-_\s]+results?\b": ["three-month-results"],
    r"\bannual[-_\s]+general[-_\s]+meeting\b": ["annual-general-meeting"],
    r"\bagm\b": ["annual-general-meeting"],
    r"\bq[1-4][-_]?\d{4}\b": ["three-month-results"],
    r"\bannounce(?:ment|s|d)?\b": ["announcement"],
    r"\bsustainability\b": ["esg"],
    r"\bgovernance\b": ["esg"],
    r"\bgreen\b": ["esg"],
    r"\benvironment\b": ["esg"],
    r"\bclimate\b": ["esg"],
    r"\bhistorical[-_\s]+information\b": ["historical-information"],
}

CONTENT_TYPE_CONCEPTS = [
    "financial_filing",
    "annual_report",
    "sec_filing",
    "10-K",
    "10-Q",
    "interim-results",
    "preliminary-results",
    "trading-update",
    "full-year-results",
    "nine-month-sales",
    "half-year-results",
    "three-month-results",
    "press-release",
    "transcript",
    "presentation",
    "webcast",
    "spreadsheet",
    "sellside-conference",
    "industry-conference",
    "investor-day-presentation",
    "news",
    "announcement",
    "seminar",
    "annual-general-meeting",
    "announcement",
    "esg",
    "historical-information"
]

def _precompute_content_type_embeddings(labels: List[str]):
    vectors = []
    for ct in labels:
        doc = nlp(ct)
        avg_vec = sum([t.vector for t in doc]) / len(doc)
        vectors.append((ct, avg_vec))
    return vectors

CONTENT_TYPE_EMBEDDINGS = _precompute_content_type_embeddings(CONTENT_TYPE_CONCEPTS)
SIMILARITY_THRESHOLD = 0.75

def _best_content_type_for_token(token_vec):
    best_label = None
    best_score = 0.0
    for ct_label, ct_vec in CONTENT_TYPE_EMBEDDINGS:
        sim = _cosine_similarity(token_vec, ct_vec)
        if sim > best_score:
            best_score = sim
            best_label = ct_label
    return best_label, best_score

# -------------------------
# Text Extraction Helpers
# -------------------------
def _extract_full_text_including_urls(html_snippet: str) -> str:
    """
    Extract visible text along with anchor texts and hrefs from the HTML snippet.
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    parts = []
    # Extract visible text
    visible_text = soup.get_text(separator=' ', strip=True)
    parts.append(visible_text)
    # Extract anchor texts and hrefs
    for a_tag in soup.find_all('a', href=True):
        anchor_text = a_tag.get_text(separator=' ', strip=True)
        if anchor_text:
            parts.append(anchor_text)
        href_val = a_tag['href']
        parts.append(href_val)
        # Clean the href for additional matching
        cleaned_href = re.sub(r'[-_/]', ' ', href_val)
        cleaned_href = re.sub(r'\.\w{2,4}$', '', cleaned_href)
        parts.append(cleaned_href)
    return " ".join(parts)

def _extract_anchor_context(anchor_tag) -> str:
    """
    Isolates the local context for a given <a> tag.
    It first finds the nearest block-level parent (div, p, li) with a minimal amount
    of text (at least 20 characters). If the immediate parent is too short, it climbs up.
    Then it removes any other links in that parent.
    """
    candidate = anchor_tag.find_parent(['div', 'p', 'li'])
    # Climb up until we get a candidate with sufficient text length.
    while candidate and len(candidate.get_text(strip=True)) < 20:
        candidate = candidate.find_parent(['div', 'p', 'li'])
    if candidate is None:
        candidate = anchor_tag  # fallback to the anchor itself if no parent is suitable
    parent_copy = BeautifulSoup(str(candidate), 'html.parser')
    for other in parent_copy.find_all('a', href=True):
        if other.get('href') != anchor_tag.get('href'):
            other.decompose()
    return str(parent_copy)

# -------------------------
# Classification Logic
# -------------------------
def _classify_snippet(html_snippet: str, forced_type: str = None) -> List[str]:
    """
    Classifies the given HTML snippet by:
      - Extracting text (including URLs)
      - Matching dictionary-based regex patterns
      - Using a similarity-based approach via spaCy
      - Returning the union of matches (and including forced_type if provided)
    """
    snippet_short = (html_snippet[:300] + '...') if len(html_snippet) > 300 else html_snippet
    logger.debug("Classifying snippet:")
    logger.debug(f"Snippet (truncated):\n{snippet_short}")
    
    text = _extract_full_text_including_urls(html_snippet)
    logger.debug(f"Extracted Text:\n{text}\n")
    
    text_lower = text.lower()
    
    dict_matches = set()
    for pattern, ct_list in CONTENT_PATTERNS.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            dict_matches.update(ct_list)
    logger.debug(f"[DICT] Found dictionary-based content types: {dict_matches}")
    
    sim_matches = set()
    doc = nlp(text_lower)
    for token in doc:
        if not token.is_alpha:
            continue
        label, sim = _best_content_type_for_token(token.vector)
        if sim >= SIMILARITY_THRESHOLD:
            sim_matches.add(label)
    logger.debug(f"[SIM] Found similarity-based content types: {sim_matches}")
    
    all_ctypes = dict_matches.union(sim_matches)
    if forced_type:
        all_ctypes.add(forced_type)
    logger.debug(f"[UNION] Final content types = {all_ctypes}")
    return list(all_ctypes)

def get_content_types_for_each_href(html_snippet: str, forced_type: str = None) -> List[List[str]]:
    """
    For every <a> tag in the HTML snippet, extract its localized context (using _extract_anchor_context)
    and classify that snippet with _classify_snippet.
    Returns a list of content type lists, one for each anchor.
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    anchors = soup.find_all('a', href=True)
    
    if not anchors:
        return [_classify_snippet(html_snippet, forced_type)]
    
    results = []
    for anchor in anchors:
        context_html = _extract_anchor_context(anchor)
        classification = _classify_snippet(context_html, forced_type)
        results.append(classification)
    return results

# -------------------------
# Main Calling Function
# -------------------------
def get_content_type_from_element(html_snippet: str, forced_type: str = None) -> Union[List[str], List[List[str]]]:
    """
    Main function to classify content types from an HTML snippet.
    
    - If the snippet contains one or more <a> tags, it returns a list of classification lists (one per link).
    - Otherwise, it returns a single list of content types for the entire snippet.
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    anchors = soup.find_all('a', href=True)
    if anchors:
        return get_content_types_for_each_href(html_snippet, forced_type)
    else:
        return _classify_snippet(html_snippet, forced_type)

# -------------------------
# Test Sample
# -------------------------
# if __name__ == "__main__":
#     sample_html = """
#     <div class="t-table">
#       <div class="t-row">
#         <div class="t-cell">
#           <div class="img-wrap">
#             <img title="Corporate Report 2024" alt="Corporate Report 2024" src="/fileadmin/symrise/images/investors/reports/2025/250327_FY24_Thumb_131x185.jpg" width="131" height="185">
#           </div>
#           <p class="news-date">March 27, 2025</p>
#           <h4>Financial Year 2024</h4>
#         </div>
#         <div class="t-cell">
#           <p><b>Downloads</b></p>
#         </div>
#       </div>
#       <div class="t-row">
#         <div class="t-cell">
#           <p>Press Release Corporate Report 2024</p>
#         </div>
#         <div class="t-cell">
#           <p>
#             <a href="/securedl/path/to/press_release.pdf" target="_blank" class="i-download">
#               pdf (218 KB)
#             </a>
#           </p>
#         </div>
#       </div>
#       <div class="t-row">
#         <div class="t-cell">
#           <p>Financial Statements 2024 (HGB - in German)</p>
#         </div>
#         <div class="t-cell">
#           <p>
#             <a href="/securedl/path/to/financial_statements.pdf" target="_blank" class="i-download">
#               pdf (3 MB)
#             </a>
#           </p>
#         </div>
#       </div>
#       <div class="t-row">
#         <div class="t-cell">
#           <p>Corporate Report 2024</p>
#         </div>
#         <div class="t-cell">
#           <p>
#             <a href="/securedl/path/to/corporate_report.pdf" target="_blank" class="i-download">
#               pdf (14 MB)
#             </a>
#           </p>
#         </div>
#       </div>
#       <div class="t-row">
#         <div class="t-cell">
#           <p>Remuneration Report 2024</p>
#         </div>
#         <div class="t-cell">
#           <p>
#             <a href="/securedl/path/to/remuneration_report.pdf" target="_blank" class="i-download">
#               pdf (353 KB)
#             </a>
#           </p>
#         </div>
#       </div>
#       <div class="t-row">
#         <div class="t-cell">
#           <p>Corporate Report 2024 (extended online version)</p>
#         </div>
#         <div class="t-cell">
#           <p>
#             <a href="https://symrise.com/corporatereport/2024/index.html" target="_blank" class="i-doc" rel="noreferrer">
#               HTML
#             </a>
#           </p>
#         </div>
#       </div>
#     </div>
#     """
#     # Call the main function with a forced type of "news"
#     output = get_content_type_from_element(sample_html, forced_type="news")
#     print("Output:")
#     if isinstance(output, list) and output and isinstance(output[0], list):
#         for idx, classification in enumerate(output, start=1):
#             print(f"Link {idx}: {classification}")
#     else:
#         print(output)