import datefinder
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_dates_from_text(text):
    # Ensure the input is a list of strings
    if isinstance(text, str):
        text = [text]
    
    extracted_dates = []
    
    for t in text:
        # Using datefinder to find dates in the text
        matches = datefinder.find_dates(t)
        
        for match in matches:
            extracted_dates.append(match)
    
    # If no dates found using datefinder, fall back to spaCy's named entity recognition (NER)
    if not extracted_dates:
        doc = nlp(' '.join(text))  # Process the text using spaCy
        for ent in doc.ents:
            if ent.label_ == "DATE":  # spaCy recognizes dates as "DATE" entities
                try:
                    # Try to parse the recognized entity to a datetime object
                    date = match.date()
                    extracted_dates.append(date)
                except ValueError:
                    continue

    return extracted_dates

# Example usage:
text = "The event is scheduled for March 21, 2025, and the fiscal year ends in December 2025."
dates = extract_dates_from_text(text)
print(dates)