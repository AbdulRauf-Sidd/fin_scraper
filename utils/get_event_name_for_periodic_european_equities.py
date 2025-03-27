import re
import spacy
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import datetime
import os
from .spacy_model import nlp

# Load spaCy's English language model
# nlp = spacy.load("en_core_web_sm")

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
    event_keywords = ["Annual Report", "Fiscal Year", "Q1", "Q2", "Q3", "Q4", "Half-year", "9M", "3M", "January - March", "January - September"]
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

def get_event_name_for_periodic_european_equities(*args):
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
    pattern_fy = r'FY\s*(\d{4})'
    pattern_half = r'(H[12])\s*(\d{4})'
    pattern_9m = r'9M\s*(\d{4})'
    pattern_3m = r'3M\s*(\d{4})'  # For 3-month results
    pattern_period_3m = r'January\s*-\s*March\s*(\d{4})'  # Detect "January - March" as 3M
    pattern_period_9m = r'January\s*-\s*September\s*(\d{4})'  # Detect "January - September" as 9M

    # Attempt regex matches (case-insensitive)
    match_fy = re.search(pattern_fy, text, re.IGNORECASE)
    match_half = re.search(pattern_half, text, re.IGNORECASE)
    match_9m = re.search(pattern_9m, text, re.IGNORECASE)
    match_3m = re.search(pattern_3m, text, re.IGNORECASE)  # Match 3M
    # match_quarter = re.search(pattern_quarter, text, re.IGNORECASE)  # Match quarter results
    match_period_3m = re.search(pattern_period_3m, text, re.IGNORECASE)  # Match "January - March"
    match_period_9m = re.search(pattern_period_9m, text, re.IGNORECASE)  # Match "January - September"

    final_event_name = None
    decision_reason = ""

    # Check for matches in a prioritized order.
    if match_fy:
        # Construct standardized event name for Fiscal Year
        year = match_fy.group(1)
        final_event_name = f"FY {year}"
        decision_reason = "Matched FY pattern via regex."
    elif match_half:
        # For half-year results, get the half (H1 or H2) and the year
        half = match_half.group(1).upper()
        year = match_half.group(2)
        final_event_name = f"{half} {year}"
        decision_reason = "Matched half-year pattern via regex."
    elif match_9m or match_period_9m:
        # If it's 9M (9-months) report
        year = match_9m.group(1) if match_9m else match_period_9m.group(1)
        final_event_name = f"9M {year}"
        decision_reason = "Matched 9M pattern via regex or period match."
    elif match_3m or match_period_3m:
        # If it's 3M (3-months) report
        year = match_3m.group(1) if match_3m else match_period_3m.group(1)
        final_event_name = f"3M {year}"
        decision_reason = "Matched 3M pattern via regex or period match."
    else:
        # Use NLP for more flexible matching
        dates, matched_keywords = extract_entities_with_spacy(text)
        
        if dates and matched_keywords:
            year = None
            for date in dates:
                # Try to extract a year from the date (if possible)
                match = re.search(r"\d{4}", date)
                if match:
                    year = match.group(0)
                    break
            
            if year:
                # Based on the event keyword found, decide the event name
                if "Annual Report" in matched_keywords or "Fiscal Year" in matched_keywords:
                    final_event_name = f"FY {year}"
                    decision_reason = "Matched 'Fiscal Year' or 'Annual Report' via NLP with identified year."
                elif "Half-year" in matched_keywords:
                    final_event_name = f"H1 {year}"  # Could be extended to detect H2 if applicable
                    decision_reason = "Matched 'Half-year' via NLP with identified year."
                elif "9M" in matched_keywords:
                    final_event_name = f"9M {year}"
                    decision_reason = "Matched '9M' via NLP with identified year."
                elif "3M" in matched_keywords:
                    final_event_name = f"3M {year}"
                    decision_reason = "Matched '3M' via NLP with identified year."
                elif any(quarter in matched_keywords for quarter in ["Q1", "Q2", "Q3", "Q4"]):
                    final_event_name = f"Quarter {year}"
                    decision_reason = "Matched quarter keyword via NLP."
        # Fallback: If no match is found via NLP or regex, handle based on content
        if not final_event_name:
            if input_source == "html":
                # In case of HTML input, return the name based on inner text or file name
                if text:
                    final_event_name = text[:50]  # Limit to the first 50 characters of the text
                    decision_reason = "No match found, using inner text as event name."
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

    # Clean the event name before returning
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
        log_entry += f"File URLs: {links}\n"
    log_entry += (f"Regex Matches -> FY: {match_fy.group(0) if match_fy else None}, "
                f"Half-Year: {match_half.group(0) if match_half else None}, "
                f"9M: {match_9m.group(0) if match_9m else None}, "
                f"3M: {match_3m.group(0) if match_3m else None}, "
                )
    log_entry += f"Final Event Name: {final_event_name}\n"
    log_entry += f"Decision Reason: {decision_reason}\n"
    log_entry += "="*50 + "\n"

    # Append log to the file (relative path, no overwrite)
    log_path = "logs/get_event_name_for_periodic_european_equities.log"
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

    # Return the cleaned final event name
    return final_event_name

# # ----- Test Example Use Calls -----

# # Test Case 1: HTML input that should match "FY YYYY"
# html_input1 = "<div><p>Company releases FY 2020 results</p><a href='https://example.com'>Link</a></div>"
# get_event_name_for_periodic_european_equities(html_input1)