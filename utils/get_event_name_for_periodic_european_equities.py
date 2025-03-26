import re
import spacy
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import datetime
import os

# Load spaCy's English language model
nlp = spacy.load("en_core_web_sm")

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
    pattern_quarter = r'Q[1-4]\s*(\d{4})'  # For Q1, Q2, Q3, Q4
    pattern_period_3m = r'January\s*-\s*March\s*(\d{4})'  # Detect "January - March" as 3M
    pattern_period_9m = r'January\s*-\s*September\s*(\d{4})'  # Detect "January - September" as 9M

    # Attempt regex matches (case-insensitive)
    match_fy = re.search(pattern_fy, text, re.IGNORECASE)
    match_half = re.search(pattern_half, text, re.IGNORECASE)
    match_9m = re.search(pattern_9m, text, re.IGNORECASE)
    match_3m = re.search(pattern_3m, text, re.IGNORECASE)  # Match 3M
    match_quarter = re.search(pattern_quarter, text, re.IGNORECASE)  # Match quarter results
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
    elif match_quarter:
        # If it's a quarterly report
        quarter = match_quarter.group(0)
        year = match_quarter.group(1)
        final_event_name = f"{quarter} {year}"
        decision_reason = "Matched quarter pattern via regex."
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
                  f"Quarter: {match_quarter.group(0) if match_quarter else None}\n")
    log_entry += f"Final Event Name: {final_event_name}\n"
    log_entry += f"Decision Reason: {decision_reason}\n"
    log_entry += "="*50 + "\n"

    # Append log to the file (relative path, no overwrite)
    log_path = "logs/get_event_name_for_periodic_european_equities.log"
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

    # Terminal output shows only the final event name.
    print(final_event_name)

# # ----- Test Example Use Calls -----

# # Test Case 1: HTML input that should match "FY YYYY"
# html_input1 = "<div><p>Company releases FY 2020 results</p><a href='https://example.com'>Link</a></div>"
# get_event_name_for_periodic_european_equities(html_input1)

# # Test Case 2: Raw event details input that matches half-year pattern "H1 YYYY"
# raw_event_name2 = "Half-year performance H1 2021"
# base_url2 = "https://chatgpt.com/sec-filings/"
# file_urls2 = ["https://chatgpt.com/sec-filings/doc1.pdf", "https://chatgpt.com/sec-filings/doc2.pdf"]
# get_event_name_for_periodic_european_equities(raw_event_name2, base_url2, file_urls2)

# # Test Case 3: HTML input that does not match any pattern (returns name based on text)
# html_input3 = "<div><p>Interim Report January - March 2024</p></div>"
# get_event_name_for_periodic_european_equities(html_input3)

# # Test Case 4: Raw event details with no matching pattern (returns raw event name)
# raw_event_name4 = "Q3 Financial Report"
# base_url4 = "https://chatgpt.com/sec-filings/"
# file_urls4 = ["https://chatgpt.com/sec-filings/doc3.pdf"]
# get_event_name_for_periodic_european_equities(raw_event_name4, base_url4, file_urls4)



# # Test Case 5:
# html_input1 = """<a target="_blank" aria-label="Open" rel="download" track_event="[&quot;download&quot;,&quot;download-document-inline-from-gallery&quot;,&quot;generic_document#2931: Y_2024_d.pdf&quot;,&quot;/en/publications/more/annual-report-2024-2931/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/931/file_en/953dcbb8e57270df70ca288218092dba4721fd63/Y_2024_e.pdf?1742480062" up-instant="false"><div class="document-tile--title">
# Annual Report 2024
# </div>
# <div class="document-tile--description">
# <time datetime="2025-03-11">03/11/2025</time>
# <span> Publication</span>
# <span>
# The Annual Report contains the combined non-financial statement of Volkswagen AG and the Volkswagen Group in accordance with sections 315c in conjunction with 289c to 289e of the HGB (Sustainability Report).
# </span>
# </div>
# </a>"""
# get_event_name_for_periodic_european_equities(html_input1)

# # Test Case 6:
# html_input1 = """<div class="document-tile gallery--item -medium" infinite_nodes_uniq_on="2936">
# <a class="document-tile--image" target="_blank" aria-label="Open" rel="download" track_event="[&quot;download&quot;,&quot;download-document-inline-from-gallery&quot;,&quot;generic_document#2936: Konzernabschluss_Volkswagen_AG_zum_31_Dezember_2024.pdf&quot;,&quot;/en/publications/more/consolidated-financial-statements-of-volkswagen-aktiengesellschaft-as-at-december-31-2024-2936/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.pdf?1741669240" up-instant="false"><img alt="Consolidated Financial Statements of Volkswagen Aktiengesellschaft as at December 31, 2024" src="https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/high_res_Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.jpg?1741669240" srcset="https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/thumb_Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.jpg?1741669240 120w 170h, https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/gallery_Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.jpg?1741669240 480w 679h, https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/high_res_Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.jpg?1741669240 595w 842h" data-sizes="auto" data-srcset="https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/thumb_Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.jpg?1741669240 120w 170h, https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/gallery_Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.jpg?1741669240 480w 679h, https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/high_res_Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.jpg?1741669240 595w 842h" class="lazyautosizes lazyloaded" decoding="async" sizes="128px">
# </a><div class="document-tile--text">
# <a target="_blank" aria-label="Open" rel="download" track_event="[&quot;download&quot;,&quot;download-document-inline-from-gallery&quot;,&quot;generic_document#2936: Konzernabschluss_Volkswagen_AG_zum_31_Dezember_2024.pdf&quot;,&quot;/en/publications/more/consolidated-financial-statements-of-volkswagen-aktiengesellschaft-as-at-december-31-2024-2936/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.pdf?1741669240" up-instant="false"><div class="document-tile--title">
# Consolidated Financial Statements of Volkswagen Aktiengesellschaft as at December 31, 2024
# </div>
# <div class="document-tile--description">
# <time datetime="2025-03-11">03/11/2025</time>
# <span> Publication</span>
# </div>
# </a><div class="document-tile--buttons icon-button-group">
# <a class="icon-button" type="button" title="Download" rel="download" track_event="[&quot;download&quot;,&quot;download-document-from-gallery&quot;,&quot;generic_document#2936: Konzernabschluss_Volkswagen_AG_zum_31_Dezember_2024.pdf&quot;,&quot;/en/publications/more/consolidated-financial-statements-of-volkswagen-aktiengesellschaft-as-at-december-31-2024-2936/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/936/file_en/04eea36bbd9693d7cfa56e958909229c3ac9a573/Consolidated_Financial_Statements_of_Volkswagen_AG_as_of_December_31_2024.pdf?1741669240&amp;disposition=attachment" up-instant="false"><span class="icon -download"></span>
# </a><button class="cart-button icon-button up-can-clean" type="button" cart-button="" data-type="generic_document" data-record="2936" title="Add to cart"><div class="icon -cart cart-button--icon"></div></button>
# <button class="share-button icon-button -initialized" type="button" title="Share"><span class="share-button--icon icon -share"></span></button><div class="share-button--popover-content"><div class="share-popover-content"><a class="btn -white share-popover-content--button -x" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-twitter&quot;,&quot;generic_document#2936: Konzernabschluss_Volkswagen_AG_zum_31_Dezember_2024.pdf&quot;,null]" href="https://twitter.com/intent/post?url=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Fconsolidated-financial-statements-of-volkswagen-aktiengesellschaft-as-at-december-31-2024-2936&amp;text=Consolidated+Financial+Statements+of+Volkswagen+Aktiengesellschaft+as+at+December+31%2C+2024+%40volkswagen" up-instant="false"><div class="icon -x"></div></a><a class="btn -white share-popover-content--button -facebook" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-facebook&quot;,&quot;generic_document#2936: Konzernabschluss_Volkswagen_AG_zum_31_Dezember_2024.pdf&quot;,null]" href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Fconsolidated-financial-statements-of-volkswagen-aktiengesellschaft-as-at-december-31-2024-2936" up-instant="false"><div class="icon -facebook"></div></a><a class="btn -white share-popover-content--button -linkedin" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-linkedin&quot;,&quot;generic_document#2936: Konzernabschluss_Volkswagen_AG_zum_31_Dezember_2024.pdf&quot;,null]" href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Fconsolidated-financial-statements-of-volkswagen-aktiengesellschaft-as-at-december-31-2024-2936" up-instant="false"><div class="icon -linkedin"></div></a><a class="btn -white share-popover-content--button -native hidden" native-share="" up-data="{&quot;url&quot;:&quot;https://www.volkswagen-group.com/en/publications/more/consolidated-financial-statements-of-volkswagen-aktiengesellschaft-as-at-december-31-2024-2936&quot;,&quot;text&quot;:&quot;Consolidated Financial Statements of Volkswagen Aktiengesellschaft as at December 31, 2024&quot;}" track_event="[&quot;sharing&quot;,&quot;share-native&quot;,&quot;generic_document#2936: Konzernabschluss_Volkswagen_AG_zum_31_Dezember_2024.pdf&quot;,null]" href="" up-instant="false"><div class="icon -etc"></div></a><a class="btn -white share-popover-content--button -email" target="_blank" native-share="hide-if-enabled" track_event="[&quot;sharing&quot;,&quot;share-email&quot;,&quot;generic_document#2936: Konzernabschluss_Volkswagen_AG_zum_31_Dezember_2024.pdf&quot;,null]" href="mailto:?body=%0AConsolidated%20Financial%20Statements%20of%20Volkswagen%20Aktiengesellschaft%20as%20at%20December%2031%2C%202024%0Ahttps%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Fconsolidated-financial-statements-of-volkswagen-aktiengesellschaft-as-at-december-31-2024-2936%0A%0A" up-instant="false"><div class="icon -email"></div></a></div></div>
# </div>
# </div>
# </div>"""
# get_event_name_for_periodic_european_equities(html_input1)


# # Test Case 6:
# html_input1 = """<div class="document-tile gallery--item -medium" infinite_nodes_uniq_on="2703">
# <a class="document-tile--image" target="_blank" aria-label="Open" rel="download" track_event="[&quot;download&quot;,&quot;download-document-inline-from-gallery&quot;,&quot;generic_document#2703: Q1_2024_d.pdf&quot;,&quot;/en/publications/more/interim-report-january-march-2024-2703/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/Q1_2024_e.pdf?1714450563" up-instant="false"><img alt="Interim Report January - March 2024" src="https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/high_res_Q1_2024_e.jpg?1714450563" srcset="https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/thumb_Q1_2024_e.jpg?1714450563 120w 170h, https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/gallery_Q1_2024_e.jpg?1714450563 480w 679h, https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/high_res_Q1_2024_e.jpg?1714450563 595w 842h" data-sizes="auto" data-srcset="https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/thumb_Q1_2024_e.jpg?1714450563 120w 170h, https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/gallery_Q1_2024_e.jpg?1714450563 480w 679h, https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/high_res_Q1_2024_e.jpg?1714450563 595w 842h" class="lazyautosizes lazyloaded" decoding="async" sizes="128px">
# </a><div class="document-tile--text">
# <a target="_blank" aria-label="Open" rel="download" track_event="[&quot;download&quot;,&quot;download-document-inline-from-gallery&quot;,&quot;generic_document#2703: Q1_2024_d.pdf&quot;,&quot;/en/publications/more/interim-report-january-march-2024-2703/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/Q1_2024_e.pdf?1714450563" up-instant="false"><div class="document-tile--title">
# Interim Report January - March 2024
# </div>
# <div class="document-tile--description">
# <time datetime="2024-04-30">04/30/2024</time>
# <span> Publication</span>
# </div>
# </a><div class="document-tile--buttons icon-button-group">
# <a class="icon-button" type="button" title="Download" rel="download" track_event="[&quot;download&quot;,&quot;download-document-from-gallery&quot;,&quot;generic_document#2703: Q1_2024_d.pdf&quot;,&quot;/en/publications/more/interim-report-january-march-2024-2703/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/703/file_en/ecbf0e4b5bee68985671226b10f71c4e32d1a2da/Q1_2024_e.pdf?1714450563&amp;disposition=attachment" up-instant="false"><span class="icon -download"></span>
# </a><button class="cart-button icon-button up-can-clean" type="button" cart-button="" data-type="generic_document" data-record="2703" title="Add to cart"><div class="icon -cart cart-button--icon"></div></button>
# <button class="share-button icon-button -initialized" type="button" title="Share"><span class="share-button--icon icon -share"></span></button><div class="share-button--popover-content"><div class="share-popover-content"><a class="btn -white share-popover-content--button -x" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-twitter&quot;,&quot;generic_document#2703: Q1_2024_d.pdf&quot;,null]" href="https://twitter.com/intent/post?url=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Finterim-report-january-march-2024-2703&amp;text=Interim+Report+January+-+March+2024+%40volkswagen" up-instant="false"><div class="icon -x"></div></a><a class="btn -white share-popover-content--button -facebook" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-facebook&quot;,&quot;generic_document#2703: Q1_2024_d.pdf&quot;,null]" href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Finterim-report-january-march-2024-2703" up-instant="false"><div class="icon -facebook"></div></a><a class="btn -white share-popover-content--button -linkedin" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-linkedin&quot;,&quot;generic_document#2703: Q1_2024_d.pdf&quot;,null]" href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Finterim-report-january-march-2024-2703" up-instant="false"><div class="icon -linkedin"></div></a><a class="btn -white share-popover-content--button -native hidden" native-share="" up-data="{&quot;url&quot;:&quot;https://www.volkswagen-group.com/en/publications/more/interim-report-january-march-2024-2703&quot;,&quot;text&quot;:&quot;Interim Report January - March 2024&quot;}" track_event="[&quot;sharing&quot;,&quot;share-native&quot;,&quot;generic_document#2703: Q1_2024_d.pdf&quot;,null]" href="" up-instant="false"><div class="icon -etc"></div></a><a class="btn -white share-popover-content--button -email" target="_blank" native-share="hide-if-enabled" track_event="[&quot;sharing&quot;,&quot;share-email&quot;,&quot;generic_document#2703: Q1_2024_d.pdf&quot;,null]" href="mailto:?body=%0AInterim%20Report%20January%20-%20March%202024%0Ahttps%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Finterim-report-january-march-2024-2703%0A%0A" up-instant="false"><div class="icon -email"></div></a></div></div>
# </div>
# </div>
# </div>"""
# get_event_name_for_periodic_european_equities(html_input1)

# # Test Case 6:
# html_input1 = """<div class="document-tile gallery--item -medium" infinite_nodes_uniq_on="2809">
# <a class="document-tile--image" target="_blank" aria-label="Open" rel="download" track_event="[&quot;download&quot;,&quot;download-document-inline-from-gallery&quot;,&quot;generic_document#2809: Q3_2024_d.pdf&quot;,&quot;/en/publications/more/interim-report-january-september-2024-2809/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/Q3_2024_e.pdf?1730264423" up-instant="false"><img alt="Interim Report January - September 2024" src="https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/high_res_Q3_2024_e.jpg?1730264423" srcset="https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/thumb_Q3_2024_e.jpg?1730264423 120w 170h, https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/gallery_Q3_2024_e.jpg?1730264423 480w 679h, https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/high_res_Q3_2024_e.jpg?1730264423 595w 842h" data-sizes="auto" data-srcset="https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/thumb_Q3_2024_e.jpg?1730264423 120w 170h, https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/gallery_Q3_2024_e.jpg?1730264423 480w 679h, https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/high_res_Q3_2024_e.jpg?1730264423 595w 842h" class="lazyautosizes lazyloaded" decoding="async" sizes="128px">
# </a><div class="document-tile--text">
# <a target="_blank" aria-label="Open" rel="download" track_event="[&quot;download&quot;,&quot;download-document-inline-from-gallery&quot;,&quot;generic_document#2809: Q3_2024_d.pdf&quot;,&quot;/en/publications/more/interim-report-january-september-2024-2809/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/Q3_2024_e.pdf?1730264423" up-instant="false"><div class="document-tile--title">
# Interim Report January - September 2024
# </div>
# <div class="document-tile--description">
# <time datetime="2024-10-30">10/30/2024</time>
# <span> Publication</span>
# </div>
# </a><div class="document-tile--buttons icon-button-group">
# <a class="icon-button" type="button" title="Download" rel="download" track_event="[&quot;download&quot;,&quot;download-document-from-gallery&quot;,&quot;generic_document#2809: Q3_2024_d.pdf&quot;,&quot;/en/publications/more/interim-report-january-september-2024-2809/capture_download&quot;]" href="https://uploads.vw-mms.de/system/production/documents/cws/002/809/file_en/216fb8a428be701afca8fe476100b2038599ae05/Q3_2024_e.pdf?1730264423&amp;disposition=attachment" up-instant="false"><span class="icon -download"></span>
# </a><button class="cart-button icon-button up-can-clean" type="button" cart-button="" data-type="generic_document" data-record="2809" title="Add to cart"><div class="icon -cart cart-button--icon"></div></button>
# <button class="share-button icon-button -initialized" type="button" title="Share"><span class="share-button--icon icon -share"></span></button><div class="share-button--popover-content"><div class="share-popover-content"><a class="btn -white share-popover-content--button -x" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-twitter&quot;,&quot;generic_document#2809: Q3_2024_d.pdf&quot;,null]" href="https://twitter.com/intent/post?url=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Finterim-report-january-september-2024-2809&amp;text=Interim+Report+January+-+September+2024+%40volkswagen" up-instant="false"><div class="icon -x"></div></a><a class="btn -white share-popover-content--button -facebook" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-facebook&quot;,&quot;generic_document#2809: Q3_2024_d.pdf&quot;,null]" href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Finterim-report-january-september-2024-2809" up-instant="false"><div class="icon -facebook"></div></a><a class="btn -white share-popover-content--button -linkedin" social-popup="true" track_event="[&quot;sharing&quot;,&quot;share-linkedin&quot;,&quot;generic_document#2809: Q3_2024_d.pdf&quot;,null]" href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Finterim-report-january-september-2024-2809" up-instant="false"><div class="icon -linkedin"></div></a><a class="btn -white share-popover-content--button -native hidden" native-share="" up-data="{&quot;url&quot;:&quot;https://www.volkswagen-group.com/en/publications/more/interim-report-january-september-2024-2809&quot;,&quot;text&quot;:&quot;Interim Report January - September 2024&quot;}" track_event="[&quot;sharing&quot;,&quot;share-native&quot;,&quot;generic_document#2809: Q3_2024_d.pdf&quot;,null]" href="" up-instant="false"><div class="icon -etc"></div></a><a class="btn -white share-popover-content--button -email" target="_blank" native-share="hide-if-enabled" track_event="[&quot;sharing&quot;,&quot;share-email&quot;,&quot;generic_document#2809: Q3_2024_d.pdf&quot;,null]" href="mailto:?body=%0AInterim%20Report%20January%20-%20September%202024%0Ahttps%3A%2F%2Fwww.volkswagen-group.com%2Fen%2Fpublications%2Fmore%2Finterim-report-january-september-2024-2809%0A%0A" up-instant="false"><div class="icon -email"></div></a></div></div>
# </div>
# </div>
# </div>"""
# get_event_name_for_periodic_european_equities(html_input1)