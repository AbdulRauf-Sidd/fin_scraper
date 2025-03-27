import re
import spacy
from .spacy_model import nlp
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import datetime
import os


def extract_text_from_html(html_element):
    """
    Uses BeautifulSoup to strip out HTML tags and return plain text, while also extracting links.
    """
    soup = BeautifulSoup(html_element, "html.parser")
    
    # Extract plain text
    text = soup.get_text(separator=" ", strip=True)
    
    # Extract URLs from <a href="..."> tags
    links = [a['href'] for a in soup.find_all('a', href=True)]
    
    return text, links  # Return both text and list of URLs

def simple_nlp_similarity(text, keyword):
    """
    A basic function to measure similarity between the input text and a keyword.
    This uses difflib's SequenceMatcher as a proxy for contextual (NLP) similarity.
    """
    return SequenceMatcher(None, text.lower(), keyword.lower()).ratio()

def extract_entities_with_spacy(text):
    """
    Use spaCy to extract entities such as dates and event types (e.g., fiscal year, quarterly reports).
    """
    doc = nlp(text)
    # Extract entities of type DATE (for year detection)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    
    # Check for specific event-related terms using keyword matching
    event_keywords = ["Annual Report", "Fiscal Year", "Q1", "Q2", "Q3", "Q4", "Quarterly", "Annual", "Yearly", "Year End", "Full Year", "First Quarter", "Second Quarter", "Third Quarter", "Fourth Quarter", "Calendar Year", "FY"] 
    matched_keywords = [keyword for keyword in event_keywords if keyword.lower() in text.lower()]
    
    return dates, matched_keywords

def clean_event_name(event_name):
    """
    Clean the event name by removing:
    - Brackets and their content
    - File extensions like .pdf, .docx, etc.
    - Any other unwanted symbols or words.
    """
    # Remove content inside brackets (e.g., [Sustainability Report])
    event_name = re.sub(r'\[.*?\]', '', event_name)
    
    # Remove file extensions (e.g., pdf, docx, xlsx, pptx, jpg, png, txt) regardless of case and with or without a dot
    event_name = re.sub(r'\.?(pdf|docx|xlsx|pptx|jpg|png|txt)', '', event_name, flags=re.IGNORECASE)
    
    # Remove any other unwanted symbols (e.g., extra spaces, special characters)
    event_name = re.sub(r'[^a-zA-Z0-9\s]', '', event_name)
    
    # Clean up extra spaces
    event_name = ' '.join(event_name.split())
    
    return event_name

def get_event_name_for_periodic_us_equities(*args):
    """
    Determines a standardized event name for European equities using NLP and regex matching.
    """
    # Determine the case based on the number of arguments
    if len(args) == 1:
        # Case 1: HTML input
        html_element = args[0]
        input_source = "html"
        text, links = extract_text_from_html(html_element)
    elif len(args) == 3:
        # Case 2: Raw event details
        raw_event_name, base_url, file_urls = args
        input_source = "raw"
        text = raw_event_name  # we use the raw event name for evaluation
        links = file_urls  # file_urls are passed here as links
    else:
        raise ValueError("Function requires either 1 or 3 parameters.")

    # Define regex patterns for standard event naming
        # Fiscal Year (FY)
    
    pattern_quarterly = r'(Q[1-4])\s*(\d{4})'
    pattern_full_year = r'(Full\s*Year|Yearly|FY|Annual|Yearly|Year\s*End|Fiscal\s*Year|Fiscal\s*Yr|FY)\s*(\d{4})'
    pattern_year_first = r'(\d{4})\s*(Full\s*Year|Yearly|FY|Annual|Year\s*End|Fiscal\s*Year|Fiscal\s*Yr|FY)'
    pattern_q1 = r'(First\s*Quarter|First-Quarter|Firstquarter|Q1|1Q).*?(\d{4})'
    pattern_reverse_q1 = r'(\d{4}).*?(First\s*Quarter|First-Quarter|Firstquarter|Q1|1Q)'
    pattern_q2 = r'(Second\s*Quarter|Second-Quarter|Secondquarter|Q2|2Q).*?(\d{4})' 
    pattern_reverse_q2 = r'(\d{4}).*?(Second\s*Quarter|Second-Quarter|Secondquarter|Q2|2Q)'
    pattern_q3 = r'(Third\s*Quarter|Third-Quarter|Thirdquarter|Q3|3Q).*?(\d{4})'
    pattern_reverse_q3 = r'(\d{4}).*?(Third\s*Quarter|Third-Quarter|Thirdquarter|Q3|3Q)'
    pattern_q4 = r'(Fourth\s*Quarter|Fourth-Quarter|Fourthquarter|Q4|4Q|4th\s*Quarter).*?(\d{4})'
    pattern_reverse_q4 = r'(\d{4}).*?(Fourth\s*Quarter|Fourth-Quarter|Fourthquarter|Q4|4Q|4th\s*Quarter)'

    full_year = r'(\d{4}).*?(Fourth\s*Quarter|Fourth-Quarter|Fourthquarter|Q4|4Q|4th\s*Quarter)'


    
  
    

    # Add additional months if needed


    # Attempt regex matches (case-insensitive)
    match_q = re.search(pattern_quarterly, text, re.IGNORECASE)
    match_full = re.search(pattern_full_year, text, re.IGNORECASE)
    match_reverse_full = re.search(pattern_year_first, text, re.IGNORECASE)
    match_q1 = re.search(pattern_q1, text, re.IGNORECASE)  # Match 3M
    match_reverse_q1 = re.search(pattern_reverse_q1, text, re.IGNORECASE)  # Match 3M
    match_q2 = re.search(pattern_q2, text, re.IGNORECASE)  # Match quarter results
    match_reverse_q2 = re.search(pattern_reverse_q2, text, re.IGNORECASE)  # Match quarter results
    match_q3 = re.search(pattern_q3, text, re.IGNORECASE)  # Match "January - March"
    match_reverse_q3 = re.search(pattern_reverse_q3, text, re.IGNORECASE)  # Match "January - March"
    match_q4 = re.search(pattern_q4, text, re.IGNORECASE)  # Match "January - September"
    match_reverse_q4 = re.search(pattern_reverse_q4, text, re.IGNORECASE)  # Match "January - September"
    
    final_event_name = None
    decision_reason = ""

    # Check for matches in a prioritized order.
    if match_q:
        # For half-year results, get the half (H1 or H2) and the year
        quarter = match_q.group(1).upper()
        year = match_q.group(2)
        final_event_name = f"{quarter} {year}"
        decision_reason = "Matched quarterly (Q1-Q4) pattern."
    elif match_full:
        # If it's 9M (9-months) report
        year = match_full.group(2)
        final_event_name = f"FY {year}"
        decision_reason = "Matched full year pattern."
    elif match_reverse_full:
        # If it's 3M (3-months) report
        year = match_q1.group(1)
        final_event_name = f"FY {year}"
        decision_reason = "Matched Full year reverse pattern."
    elif match_q1:
        # If it's 3M (3-months) report
        year = match_q1.group(2)
        final_event_name = f"Q1 {year}"
        decision_reason = "Matched Q1 pattern."
    elif match_q2:
        # If it's 3M (3-months) report
        year = match_q3.group(2)
        final_event_name = f"Q2 {year}"
        decision_reason = "Matched Q2 pattern."
    elif match_q3:
        # If it's 3M (3-months) report
        year = match_q3.group(2)
        final_event_name = f"Q3 {year}"
        decision_reason = "Matched Q3 pattern."
    elif match_q4:
        # If it's 3M (3-months) report
        year = match_q4.group(2)
        final_event_name = f"Q4 {year}"
        decision_reason = "Matched Q4 pattern."
    elif match_reverse_q1:
        # If it's 3M (3-months) report
        year = match_reverse_q1.group(1)
        final_event_name = f"Q1 {year}"
        decision_reason = "Matched Q1 reverse pattern."
    elif match_reverse_q2:
        # If it's 3M (3-months) report
        year = match_reverse_q2.group(1)
        final_event_name = f"Q2 {year}"
        decision_reason = "Matched Q2 reverse pattern."
    elif match_reverse_q3:
        # If it's 3M (3-months) report
        year = match_reverse_q3.group(1)
        final_event_name = f"Q3 {year}"
        decision_reason = "Matched Q3 reverse pattern."
    elif match_reverse_q4:
        # If it's 3M (3-months) report
        year = match_reverse_q4.group(1)
        final_event_name = f"Q4 {year}"
        decision_reason = "Matched Q4 reverse pattern."
    else:
        # Use NLP for more flexible matching
        dates, matched_keywords = extract_entities_with_spacy(text)
        
        if dates and matched_keywords:
            year = None
            for date in dates:
                # Extract year from date (if available)
                match = re.search(r"\d{4}", date)
                if match:
                    year = match.group(0)
                    break
            
            if year:
                # Standardize event name based on matched keywords
                if "Annual Report" in matched_keywords or "Fiscal Year" in matched_keywords:
                    final_event_name = f"FY {year}"
                    decision_reason = "Matched 'Annual Report' or 'Fiscal Year' with extracted year."

                elif any(q in matched_keywords for q in ["Q1", "First Quarter"]):
                    final_event_name = f"Q1 {year}"
                    decision_reason = "Matched 'Q1' or 'First Quarter' keyword."

                elif any(q in matched_keywords for q in ["Q2", "Second Quarter"]):
                    final_event_name = f"Q2 {year}"
                    decision_reason = "Matched 'Q2' or 'Second Quarter' keyword."

                elif any(q in matched_keywords for q in ["Q3", "Third Quarter"]):
                    final_event_name = f"Q3 {year}"
                    decision_reason = "Matched 'Q3' or 'Third Quarter' keyword."

                elif any(q in matched_keywords for q in ["Q4", "Fourth Quarter"]):
                    final_event_name = f"Q4 {year}"
                    decision_reason = "Matched 'Q4' or 'Fourth Quarter' keyword."

                elif "Quarterly" in matched_keywords:
                    final_event_name = f"Quarterly {year}"
                    decision_reason = "Matched generic 'Quarterly' keyword."

                else:
                    final_event_name = None
                    decision_reason = "No specific periodic keyword matched."
            else:
                final_event_name = None
                decision_reason = "No year extracted from dates."
        else:
            final_event_name = None
            decision_reason = "Insufficient data (missing dates or keywords)."
        # Fallback: If no match is found via NLP or regex, handle based on content
        if not final_event_name:
            if input_source == "html":
                # In case of HTML input, return the name based on inner text or file name
                if text:
                    final_event_name = text  # Limit to the first 50 characters of the text
                    decision_reason = "No match found, using inner text as event name."
                    print('djksajdkasjdks')
                elif links:
                    # If links exist, extract the file name and use it
                    file_name = links[0].split("/")[-1].split("?")[0]
                    final_event_name = file_name
                    decision_reason = "No match found, using file name from link as event name."
                else:
                    final_event_name = None
                    decision_reason = "No match found, and no relevant text or links."
            else:
                final_event_name = raw_event_name
                decision_reason = "No match found, returning raw event name for raw input."


    final_event_name = clean_event_name(final_event_name)

    # Build a log entry with separators and timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = "\n" + "="*50 + "\n"
    log_entry += f"Timestamp: {timestamp}\n"
    log_entry += f"Input Source: {input_source}\n"
    if input_source == "html":
        log_entry += f"HTML Input: {html_element}\n"
        log_entry += f"Extracted Text: {text}\n"
        log_entry += f"Extracted Links: {links}\n"
    else:
        log_entry += f"Raw Event Name: {raw_event_name}\n"
        log_entry += f"Base URL: {base_url}\n"
    #     log_entry += f"File URLs: {links}\n"
    # log_entry += (f"Regex Matches -> FY: {match_fy.group(0) if match_fy else None}, "
    #               f"Half-Year: {match_half.group(0) if match_half else None}, "
    #               f"9M: {match_9m.group(0) if match_9m else None}, "
    #               f"3M: {match_3m.group(0) if match_3m else None}, "
    #               )
    log_entry += f"Final Event Name: {final_event_name}\n"
    log_entry += f"Decision Reason: {decision_reason}\n"
    log_entry += "="*50 + "\n"

    # Append log to the file (relative path, no overwrite)
    log_path = "logs/get_event_name_for_periodic_european_equities.log"
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

    # Terminal output shows only the final event name.
    # print(final_event_name)
    return final_event_name


# print(get_event_name_for_periodic_us_equities(''' <div class="list__content" bis_skin_checked="1"><h3><a href="/news/press-releases/PVH-Corp-Reports-2024-Third-Quarter-Revenue-and-Earnings-Above-Guidance">PVH Corp. Reports 2024 Third Quarter Revenue and Earnings Above Guidance</a></h3><p class="list__description">Third quarter Revenue: Decreased 5% to $2.255 billion compared to the prior year period (decreased 6% on a constant currency basis), and exceeded guidance of a decrease of 6% to 7% (decrease of 7% to 8% on a constant currency basis) EPS: GAAP basis: $2.34 exceeded guidance of approximately $2.30</p><!----><p class="list__date">Dec 04, 2024</p></div>'''))
