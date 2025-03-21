import spacy
from bs4 import BeautifulSoup

# Load the pre-trained SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

def refine_event_name(raw_name):
    """
    Refine the raw event name extracted by filtering out irrelevant words or fragments.
    Uses SpaCy's part-of-speech tagging to remove non-noun tokens like verbs and adjectives.
    
    Arguments:
    raw_name -- the initially extracted raw event name string.
    
    Returns:
    refined_name -- the filtered event name with only relevant entities.
    """
    # Process the raw name again with SpaCy
    doc = nlp(raw_name)

    # Define a list of irrelevant words or fragments to discard
    discard_keywords = [
        "view", "webcast", "session", "presentation", "video", "online", "stream", 
        "sep", "am", "pm", "edt", "pdt", "conference", "event", "schedule", "live", 
        "broadcast", "watch", "date", "details", "link", "forum", "webinar", "details"
    ]
    
    # Filter tokens: keep only proper nouns, event-related terms, and named entities
    refined_tokens = [
        token.text for token in doc 
        if (token.pos_ == 'PROPN' or token.pos_ == 'NOUN') and token.text.lower() not in discard_keywords
    ]

    # Reconstruct the refined event name from the remaining tokens
    refined_name = " ".join(refined_tokens)

    # Return a cleaned-up version of the event name
    return refined_name.strip()

def extract_event_name(text):
    """
    Extract event names from the given HTML or plain text using NLP techniques (SpaCy NER).
    First, remove HTML tags using BeautifulSoup.

    Arguments:
    text -- the input string or list of strings that may contain event information.

    Returns:
    event_name -- extracted event name or None if not found.
    """
    # If the input is a list of strings, combine them
    if isinstance(text, list):
        text = " ".join(text)

    # Clean the HTML tags from the input text (if any)
    soup = BeautifulSoup(text, "html.parser")
    cleaned_text = soup.get_text()

    # Process the cleaned text with SpaCy NLP model
    doc = nlp(cleaned_text)

    # Extract potential event names (using named entities)
    event_names = []
    for ent in doc.ents:
        # We are looking for named entities that might be event names, such as 'ORG', 'EVENT', 'WORK_OF_ART'
        if ent.label_ in ['ORG', 'EVENT', 'WORK_OF_ART']:  # These labels are more likely to be event-related
            raw_event_name = ent.text.strip()
            refined_event_name = refine_event_name(raw_event_name)
            event_names.append(refined_event_name)

    # If we have multiple event names, deduplicate and choose the most relevant one
    if event_names:
        # Remove duplicates by converting the list to a set, then back to a list
        event_names = list(set(event_names))

        # Choose the longest event name as the most likely candidate (more complete)
        event_name = max(event_names, key=len)
        return event_name.strip()
    
    # If no event name found, return None
    return None

# Test examples
test_inputs = [
    '<li class="list_item"><!----><div class="listcontent"><h3> Goldman Sachs Global Retailing Conference </h3><!----><p class="listdescription listwebcast_link"><a href="javascript:void(window.open(https://event.webcasts.com/starthere.jsp?ei=1685908&amp;tp_key=b9e65c5ffc&amp;tp_special=8,Window1,menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes));">View Webcast</a></p><p class="list_date"> Sep 05, 2024 10:20am EDT / 7:20am PDT </p></div></li>',
    '<div><p> Join us for the Amazing Online Event on Sep 15, 2024. View details and stream live! </p></div>',
    'Webcast for the Tech Expo 2024 on September 23.',
    '<p> The Goldman Sachs Global Retailing Conference event will be held on October 5, 2024. Join us! </p>'
]

event_name = extract_event_name(test_inputs)
if event_name:
    print(f"Extracted Event Name: {event_name}")
else:
    print("No event name found")