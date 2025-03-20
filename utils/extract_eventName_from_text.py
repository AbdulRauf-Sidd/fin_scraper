import spacy
from bs4 import BeautifulSoup

# Load the pre-trained SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

def refine_event_name(raw_name):
    """
    Refine the raw event name extracted by filtering out irrelevant words or fragments.
    
    Arguments:
    raw_name -- the initially extracted raw event name string.
    
    Returns:
    refined_name -- the filtered event name with only relevant entities.
    """
    # Process the raw name again with SpaCy
    doc = nlp(raw_name)

    # Define a list of words or fragments to discard
    discard_words = ["view", "webcast", "sep", "webcast", "am", "pm", "edt", "pdt", "video", "stream", "online"]

    # Filter out tokens that are in the discard list and not relevant
    refined_tokens = [token.text for token in doc if token.text.lower() not in discard_words]

    # Reconstruct the refined event name from the remaining tokens
    refined_name = " ".join(refined_tokens)

    return refined_name.strip()

def extract_event_name(text):
    """
    Extract event names from the given HTML or plain text using NLP techniques (SpaCy NER).
    First, remove HTML tags using BeautifulSoup.

    Arguments:
    text -- the input string that may contain event information.

    Returns:
    event_name -- extracted event name or None if not found.
    """
    # Clean the HTML tags from the input text
    soup = BeautifulSoup(text, "html.parser")
    cleaned_text = soup.get_text()

    # Process the cleaned text with SpaCy NLP model
    doc = nlp(cleaned_text)

    # Check if any named entities match event-related categories
    for ent in doc.ents:
        # We are looking for named entities that might be event names, such as 'ORG', 'EVENT', 'WORK_OF_ART'
        if ent.label_ in ['ORG', 'EVENT', 'WORK_OF_ART']:  # These labels are more likely to be event-related
            # Further refinement: Re-run the extraction on the raw name
            raw_event_name = ent.text.strip()
            refined_event_name = refine_event_name(raw_event_name)
            return refined_event_name  # Return the refined event name

    # If no event name found, return None
    return None

# Test examples
test_inputs = [
    '<li class="list_item"><!----><div class="listcontent"><h3> Goldman Sachs Global Retailing Conference </h3><!----><p class="listdescription listwebcast_link"><a href="javascript:void(window.open(https://event.webcasts.com/starthere.jsp?ei=1685908&amp;tp_key=b9e65c5ffc&amp;tp_special=8,Window1,menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes));">View Webcast</a></p><p class="list_date"> Sep 05, 2024 10:20am EDT / 7:20am PDT </p></div></li>'
]

# Extract event names for each input
for text in test_inputs:
    event_name = extract_event_name(text)
    print(f"Extracted Event Name: {event_name}")





# import spacy
# from bs4 import BeautifulSoup

# # Load the pre-trained SpaCy NLP model
# nlp = spacy.load("en_core_web_sm")

# def extract_event_name(text):
#     """
#     Extract event names from the given HTML or plain text using NLP techniques (SpaCy NER).
#     First, remove HTML tags using BeautifulSoup.

#     Arguments:
#     text -- the input string that may contain event information.

#     Returns:
#     event_name -- extracted event name or None if not found.
#     """
#     # Clean the HTML tags from the input text
#     soup = BeautifulSoup(text, "html.parser")
#     cleaned_text = soup.get_text()

#     # Process the cleaned text with SpaCy NLP model
#     doc = nlp(cleaned_text)

#     # Check if any named entities match event-related categories
#     for ent in doc.ents:
#         # We are looking for named entities that might be event names, such as 'ORG', 'EVENT', 'WORK_OF_ART'
#         if ent.label_ in ['ORG', 'EVENT', 'WORK_OF_ART']:  # These labels are more likely to be event-related
#             return ent.text.strip()  # Return the entity as the event name

#     # If no event name found, return None
#     return None

# # Test examples
# test_inputs = [
#     '<li class="list_item"><!----><div class="listcontent"><h3> Goldman Sachs Global Retailing Conference </h3><!----><p class="listdescription listwebcast_link"><a href="javascript:void(window.open(https://event.webcasts.com/starthere.jsp?ei=1685908&amp;tp_key=b9e65c5ffc&amp;tp_special=8,Window1,menubar=no,statusbar=no, width=800,height=600,toolbar=no,scrollbars=yes));">View Webcast</a></p><p class="list_date"> Sep 05, 2024 10:20am EDT / 7:20am PDT </p></div></li>'
# ]

# # Extract event names for each input
# for text in test_inputs:
#     event_name = extract_event_name(text)
#     print(f"Extracted Event Name: {event_name}")