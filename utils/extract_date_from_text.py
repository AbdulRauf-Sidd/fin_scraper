import re
import dateparser
import spacy

# Load SpaCy model for named entity recognition
nlp = spacy.load("en_core_web_sm")

def extract_event_date_from_html(text):
    # Regular expression to match date formats like "Sep 05, 2024 10:20am EDT"
    date_pattern = r'\b([A-Za-z]{3}\s\d{2},\s\d{4})\s(\d{1,2}:\d{2}[ap]m)\s([A-Z]{3,4})'
    
    # Search for dates in the input text using regex
    match = re.search(date_pattern, text)
    
    if match:
        # Extract the matched date (month day, year time zone and time)
        extracted_date = match.group(0)
        
        # Use dateparser to parse the extracted date string
        parsed_date = dateparser.parse(extracted_date)
        
        # Return the parsed date if successfully parsed
        if parsed_date:
            return parsed_date
        
    # If regex fails, use SpaCy to extract possible date entities from the text
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    
    if dates:
        for date in dates:
            # Parse any date found by SpaCy
            parsed_date = dateparser.parse(date)
            if parsed_date:
                return parsed_date
    
    # If no date is found, return None
    return None

# Test with your input example
input_text = '''<li class="list_item"><!----><div class="listcontent"><h3> Goldman Sachs Global Retailing Conference </h3><!----><p class="listdescription listwebcast_link"><a href="javascript:void(window.open(https://event.webcasts.com/starthere.jsp?ei=1685908&amp;tp_key=b9e65c5ffc&amp;tp_special=8,Window1,menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes));">View Webcast</a></p><p class="list_date"> Sep 05, 2024 10:20am EDT / 7:20am PDT </p></div></li>'''

extracted_date = extract_event_date_from_html(input_text)
print(f"Extracted Event Date: {extracted_date}")
