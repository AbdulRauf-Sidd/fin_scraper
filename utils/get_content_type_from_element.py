import re
import logging
import math
import spacy
from bs4 import BeautifulSoup
from typing import List, Dict, Set
from spacy_model import nlp

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
## SPAcy + Embeddings ##
#######################

# def load_spacy_model(model_name: str = "en_core_web_md"):
#     """
#     Loads spaCy model for vector similarity.
#     """
#     logger.info(f"Loading spaCy model: {model_name}")
#     nlp_loaded = spacy.load(model_name)
#     logger.info("spaCy model loaded successfully.")
#     return nlp_loaded

# nlp = load_spacy_model()

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

##############################
## CONTENT TYPE DICTIONARY  ##
##############################

# Updated dictionary with more flexible patterns:
# - "filings?" for singular/plural
# - "reports?" for singular/plural
# - "financials?" -> "financial_filing"
# Use re.IGNORECASE so we don't need to do explicit .lower() checks in the pattern itself.
CONTENT_PATTERNS: Dict[str, List[str]] = {
    # exact or partial matches
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

##############################
## SIMILARITY-BASED FALLBACK ##
##############################

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
SIMILARITY_THRESHOLD = 0.75  # can raise or lower

def _best_content_type_for_token(token_vec):
    """
    Return (content_type_label, similarity) with the highest similarity
    from our known list of content types.
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
    Extracts a string from the HTML snippet containing:
    - visible text
    - anchor text
    - hrefs from <a> tags, cleaned and tokenized
    """
    soup = BeautifulSoup(html_snippet, 'html.parser')
    parts = []

    # 1) Visible text
    visible_text = soup.get_text(separator=' ', strip=True)
    parts.append(visible_text)

    # 2) Anchor text + hrefs
    for a_tag in soup.find_all('a', href=True):
        anchor_text = a_tag.get_text(separator=' ', strip=True)
        if anchor_text:
            parts.append(anchor_text)

        href_val = a_tag['href']
        parts.append(href_val)

        # NEW: Break href into components to allow regex & NLP match
        # Replace delimiters with space, remove extensions like .pdf
        cleaned_href = re.sub(r'[-_/]', ' ', href_val)  # split common delimiters
        cleaned_href = re.sub(r'\.\w{2,4}$', '', cleaned_href)  # remove file extensions like .pdf, .docx
        parts.append(cleaned_href)

    full_text = " ".join(parts)
    return full_text



##############################
## MAIN CONTENT-TYPE METHOD ##
##############################

def get_content_type_from_element(
    html_snippet: str,
    forced_type: str = None
) -> List[str]:
    """
    1) Extract full text from the snippet ...
    2) Dictionary-based approach ...
    3) Similarity approach ...
    4) Union them.
    5) If forced_type is provided, add it to the final set.
    """
    # Log a condensed snippet
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
        # We do re.IGNORECASE so we can handle different cases if we choose not to force .lower() on the pattern
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

    # -- 3) Union
    all_ctypes = dict_matches.union(sim_matches)
    if forced_type:  # i.e., if forced_type is not None or empty
        all_ctypes.add(forced_type)

    logger.debug(f"[UNION] Final content types = {all_ctypes}")
    return list(all_ctypes)

# ########################
# ##  DEMO / EXAMPLE    ##
# ########################
# if __name__ == "__main__":
#     # print(get_content_type_from_element("PVH Corp. Reports 2020 Third Quarter Results and Provides Update Relating to the Impact of the Pandemic"))
#     # Test with your input example
#     input_text = [
#         "\n    <article data-url=\"/content/dsm-firmenich/en/investors/historical-information/corporate-governance/agm/annual-general-meeting-2023.html\" class=\" non-cta\">\n        \n        \n        \n        <div class=\"content\">\n            <span class=\"cmp-list__item-arrow\">\n                <em class=\"icon-arrow-narrow-right\"></em>\n            </span>\n            \n            \n            \n                <h4 class=\"cmp-list__item-title no-desc\">\n                    \n                    \n                        <a title=\"Annual General Meeting of Shareholders 2023 | DSM\" href=\"/en/investors/historical-information/corporate-governance/agm/annual-general-meeting-2023.html\">Annual General Meeting of Shareholders 2023 | DSM</a>\n                    \n                </h4>\n            \n            \n            \n        </div>\n    </article>\n\n"
#     ]
#     for x in input_text:
#         print(x)
#         ctypes = get_content_type_from_element(x, "news")
#         print("Content Types Detected:", ctypes)
#         print("\n")