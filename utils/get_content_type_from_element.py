import re
import logging
import math
import spacy
from bs4 import BeautifulSoup
from typing import List, Dict, Set
from .spacy_model import nlp

#######################
## LOGGING SETUP     ##
#######################

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/get_content_trype_from_element.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

#######################
## UTILITY FUNCTIONS ##
#######################

def _cosine_similarity(vec_a, vec_b):
    """
    Compute cosine similarity between two vectors.
    """
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

##############################
## CONTENT TYPE DICTIONARY  ##
##############################

CONTENT_PATTERNS: Dict[str, List[str]] = {
    r"\b10[-_\s]?k\b":                       ["10-K", "sec-filing"],
    r"\b10[-_\s]?q\b":                       ["10-Q", "sec-filing"],
    r"\bannual[-_\s]+report\b":              ["annual-report"],
    r"\bsec[-_\s]+filings?\b":               ["sec-filing"],
    r"\bfinancials?\b":                      ["financial-filing"],
    r"\breports?\b":                         ["financial-filing"],
    r"\bearnings[-_\s]+release\b":           ["financial-filing"],
    r"\bpress[-_\s]+release\b":              ["press-release"],
    r"\bpresentation\b":                     ["presentation"],
    r"\btranscript\b":                       ["transcript"],
    r"\bwebcast\b":                          ["webcast"],
    r"\bspreadsheet\b":                      ["spreadsheet"],
    r"\bsellside[-_\s]+conference\b":        ["sellside-conference"],
    r"\bindustry[-_\s]+conference\b":        ["industry-conference"],
    r"\binvestor[-_\s]+day[-_\s]+presentation\b": ["investor-day-presentation"],
    r"\bpreliminary[-_\s]+results?\b":       ["preliminary-results"],
    r"\binterim[-_\s]+results?\b":           ["interim-results"],
    r"\btrading[-_\s]+update\b":             ["trading-update"],
    r"\bfull[-_\s]?year[-_\s]+results?\b":   ["full-year-results"],
    r"\bnine[-_\s]?month[-_\s]+sales?\b":    ["nine-month-sales"],
    r"\bhalf[-_\s]?year[-_\s]+results?\b":   ["half-year-results"],
    r"\bthree[-_\s]?month[-_\s]+results?\b": ["three-month-results"],   
    r"\bannual[-_\s]+general[-_\s]+meeting\b": ["annual-general-meeting"],
    r"\bagm\b":                              ["annual-general-meeting"],
    r"\bq[1-4][-_]?\d{4}\b":                 ["three-month-results"],
    r"\btrading[-_\s]+update\b":             ["trading-update"],
    r"\bannounce(?:ment|s|d)?\b":            ["announcement"],
}

#################################
## SIMILARITY-BASED FALLBACK   ##
#################################

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
    "announcement"
]

def _precompute_content_type_embeddings(labels: List[str]):
    """
    For each content type label, compute the average spaCy vector.
    """
    vectors = []
    for ct in labels:
        doc = nlp(ct)
        avg_vec = sum([t.vector for t in doc]) / len(doc)
        vectors.append((ct, avg_vec))
    return vectors

CONTENT_TYPE_EMBEDDINGS = _precompute_content_type_embeddings(CONTENT_TYPE_CONCEPTS)
SIMILARITY_THRESHOLD = 0.75  # Adjust this threshold as needed

def _best_content_type_for_token(token_vec):
    """
    Return the (content_type_label, similarity) with the highest similarity.
    """
    best_label = None
    best_score = 0.0
    for ct_label, ct_vec in CONTENT_TYPE_EMBEDDINGS:
        sim = _cosine_similarity(token_vec, ct_vec)
        if sim > best_score:
            best_score = sim
            best_label = ct_label
    return best_label, best_score

##################
## TEXT PARSING ##
##################

def _extract_full_text_including_urls(html_snippet: str) -> str:
    """
    Extract a string from the HTML snippet containing:
    - Visible text.
    - Anchor text.
    - Hrefs from <a> tags (including a cleaned version for additional matching).
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    parts = []

    # Visible text
    visible_text = soup.get_text(separator=' ', strip=True)
    parts.append(visible_text)

    # Anchor text and hrefs
    for a_tag in soup.find_all('a', href=True):
        anchor_text = a_tag.get_text(separator=' ', strip=True)
        if anchor_text:
            parts.append(anchor_text)
        href_val = a_tag['href']
        parts.append(href_val)
        # Clean href by splitting on delimiters and removing common file extensions
        cleaned_href = re.sub(r'[-_/]', ' ', href_val)
        cleaned_href = re.sub(r'\.\w{2,4}$', '', cleaned_href)
        parts.append(cleaned_href)

    full_text = " ".join(parts)
    return full_text

##############################
## MAIN CONTENT-TYPE METHOD ##
##############################

def get_individual_content_type_from_element(
    html_snippet: str,
    forced_type: str = None
) -> List[str]:
    """
    Extract content types from the given HTML snippet.
    
    Steps:
    1) Extract full text (including cleaned-up URLs).
    2) Apply a dictionary-based approach using regex patterns.
    3) Apply a similarity-based approach using spaCy embeddings.
    4) Return the union of content types found, and include forced_type if provided.
    """
    snippet_short = (html_snippet[:300] + '...') if len(html_snippet) > 300 else html_snippet
    logger.debug("\n----------------------------------------------------")
    logger.debug(f"Raw HTML Snippet (truncated):\n{snippet_short}")
    logger.debug("----------------------------------------------------")

    text = _extract_full_text_including_urls(html_snippet)
    logger.debug(f"Extracted Text:\n{text}\n")

    text_lower = text.lower()

    # -- 1) Dictionary approach
    dict_matches = set()
    for pattern, ct_list in CONTENT_PATTERNS.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            for ctype in ct_list:
                dict_matches.add(ctype)
    logger.debug(f"[DICT] Found dictionary-based content types: {dict_matches}")

    # -- 2) Similarity approach
    sim_matches = set()
    doc = nlp(text_lower)
    for token in doc:
        if not token.is_alpha:
            continue
        label, sim = _best_content_type_for_token(token.vector)
        if sim >= SIMILARITY_THRESHOLD:
            sim_matches.add(label)
    logger.debug(f"[SIM] Found similarity-based content types: {sim_matches}")

    # -- 3) Union of the two methods
    all_ctypes = dict_matches.union(sim_matches)
    if forced_type:
        all_ctypes.add(forced_type)
    logger.debug(f"[UNION] Final content types = {all_ctypes}")
    return list(all_ctypes)

def get_content_type_from_element(
    html_snippet: str,
    forced_type: str = None
) -> List[List[str]]:
    """
    For each <a> tag (i.e., each href) in the HTML snippet, generate a content type
    classification list using the shared content (outside of links) along with
    only the current <a> tag's anchor text and href.
    
    This ensures that we do not unionize content types across different document links.
    
    Returns:
        A list of lists where each inner list corresponds to the content types for
        the respective <a> tag (in the order they appear in the HTML snippet).
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    anchors = soup.find_all('a', href=True)
    
    # If no <a> tags are found, fallback to processing the entire snippet.
    if not anchors:
        return [get_individual_content_type_from_element(html_snippet, forced_type)]
    
    result = []
    
    # Process each <a> tag individually.
    for i, _ in enumerate(anchors):
        # Create a fresh copy of the entire soup.
        soup_copy = BeautifulSoup(str(soup), 'html.parser')
        anchors_copy = soup_copy.find_all('a', href=True)
        
        # Remove all <a> tags except the one at the current index.
        for j, a_copy in enumerate(anchors_copy):
            if j != i:
                a_copy.decompose()  # Remove this tag entirely.
        
        # Convert the modified soup back into a string.
        modified_html = str(soup_copy)
        
        # Get content types using the same classification logic.
        content_types = get_individual_content_type_from_element(modified_html, forced_type)
        result.append(content_types)
    
    return result

########################
##  DEMO / EXAMPLE    ##
########################

# Uncomment the following block to test the functionality.
# if __name__ == "__main__":
#     input_text = """
#     <article data-url="/content/dsm-firmenich/en/investors/historical-information/corporate-governance/agm/annual-general-meeting-2023.html" class=" non-cta">
#         <div class="content">
#             <span class="cmp-list__item-arrow">
#                 <em class="icon-arrow-narrow-right"></em>
#             </span>
#             <h4 class="cmp-list__item-title no-desc">
#                 <a title="Annual General Meeting of Shareholders 2023 | DSM" href="/en/investors/historical-information/corporate-governance/agm/annual-general-meeting-2023.html">
#                     Annual General Meeting of Shareholders 2023 | DSM
#                 </a>
#             </h4>
#             <a title="Presentation Document" href="/docs/presentation.pdf">Presentation</a>
#         </div>
#     </article>
#     """
#     content_types_lists = get_content_type_from_element(input_text, forced_type="news")
#     print("Content Types for each link:")
#     for ct_list in content_types_lists:
#         print(ct_list)