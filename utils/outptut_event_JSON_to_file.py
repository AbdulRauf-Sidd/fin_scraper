import logging
from get_content_type_from_element import get_content_type_from_element
from get_date_from_element import get_date_from_element
from get_event_name_from_element import get_event_name_from_element
from get_url_from_element import get_urls_from_element
from typing import Optional, List, Dict
import json
from utils import download_file
logger = logging.getLogger(__name__)

# Hypothetical imports of your extraction functions (adjust as needed)
# from my_extraction_module import get_event_name_from_element, get_date_from_element, get_content_type_from_element

def construct_event_json(
    html_element: str,
    equity_ticker: str,
    geography: str,
    periodicity: str,
    base_url: str = "https://www.pvh.com/",
    # Optionally you could accept a list if you want multiple data items:
    # published_dates: List[str] = None,
    # content_types: List[List[str]] = None,
) -> Optional[Dict]:
    """
    Construct the JSON structure:
    {
        "event_name": {event_name},
        "equity_ticker": {equity_ticker},
        "geography": {geography},
        "periodicity": {periodicity},
        "data": [
            {
                "file_name": "Moiz",     # temporarily not None, so skip logic won't fire
                "file_type": null,
                "published_date": "YYYY-MM-DD",
                "r2_path": null,
                "content_type": [...multiple content types...]
            },
            ...
        ]
    }

    Skip returning JSON (return None) if:
    - event_name is None/empty
    - OR if no valid data object remains (e.g., if file_name is None or empty => skip that data object)
    """
    logger.debug("Starting construct_event_json function.")
    logger.debug(f"html_element length={len(html_element)}")
    logger.debug(f"equity_ticker={equity_ticker}, geography={geography}, periodicity={periodicity}")

    # ~~~~~~~~~~~~~~~~~~~~~~
    # 1) Extract fields
    # ~~~~~~~~~~~~~~~~~~~~~~

    event_name = get_event_name_from_element(html_element)
    logger.debug(f"Extracted event_name={event_name}")

    published_date = get_date_from_element(html_element)
    logger.debug(f"Extracted published_date={published_date}")

    content_type = get_content_type_from_element(html_element)
    logger.debug(f"Extracted content_type={content_type}")

    # If event_name is missing or empty, skip entirely
    if not event_name:
        logger.debug("No event_name found. Skipping JSON construction -> return None.")
        return None

    # ~~~~~~~~~~~~~~~~~~~~~~
    # 2) Build "data" array
    # ~~~~~~~~~~~~~~~~~~~~~~

    # For now, we assume only one data object. 
    # If you need multiple, you can loop over a list of published_dates / content_types.
    # We'll build one data dict:
    data_objects = []

    # Let’s define file_name = "Moiz" so that it's never None
    file_name = "Moiz"   # placeholder
    file_type = None
    r2_path = None
    file_url = get_urls_from_element(html_element, base_url)

    # If file_name is None => skip. But we just forced it to "Moiz."
    if file_name:
        # Build the data object
        single_data = {
            "file_name": file_name,
            "file_type": file_type,
            "published_date": published_date if published_date else "",  # or "Null"
            "r2_path": r2_path,
            "url": file_url,
            "content_type": content_type if content_type else []
        }
        data_objects.append(single_data)
        logger.debug(f"Constructed data object: {single_data}")
    else:
        logger.debug("file_name is None -> skip adding data object")

    # If after this logic we have no data objects, skip returning JSON
    if len(data_objects) == 0:
        logger.debug("No valid data objects in 'data'. Skipping -> return None.")
        return None

    # ~~~~~~~~~~~~~~~~~~~~~~
    # 3) Build final JSON
    # ~~~~~~~~~~~~~~~~~~~~~~

    result_json = {
        "event_name": event_name,
        "equity_ticker": equity_ticker,
        "geography": geography,
        "periodicity": periodicity,
        "data": data_objects
    }

    logger.debug(f"Constructed final JSON: {result_json}")

    # ~~~~~~~~~~~~~~~~~~~~~~
    # 4) Return
    # ~~~~~~~~~~~~~~~~~~~~~~
    logger.debug("Returning constructed JSON.")
    return result_json

def output_event_JSON_to_file(
    input_json_file: str,
    output_json_file: str,
    equity_ticker: str,
    geography: str,
    periodicity: str
) -> None:
    """
    1) Reads a JSON file containing an array of HTML snippets
    2) For each snippet, calls 'construct_event_json'
    3) Collects valid JSON returns
    4) Writes them to 'output_json_file' in a single list
    """

    # ~~~~~ 1) Read the input JSON ~~~~~
    with open(input_json_file, "r", encoding="utf-8") as f:
        snippet_list = json.load(f)

    logger.info(f"Loaded {len(snippet_list)} snippets from {input_json_file}")

    # ~~~~~ 2) Process each snippet ~~~~~
    final_results = []

    for idx, snippet in enumerate(snippet_list, start=1):
        logger.info(f"Processing snippet #{idx} / {len(snippet_list)}")
        # We assume 'construct_event_json' is imported or defined in the same file
        result = construct_event_json(
            html_element=snippet,
            equity_ticker=equity_ticker,
            geography=geography,
            periodicity=periodicity
        )

        if result is None:
            logger.info(f"Snippet #{idx} -> Skipped (None returned).")
        else:
            logger.info(f"Snippet #{idx} -> Event JSON created.")
            final_results.append(result)

    # ~~~~~ 3) Write valid results to 'output_json_file' ~~~~~
    with open(output_json_file, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2)

    logger.info(f"Done! Wrote {len(final_results)} items to {output_json_file}")

#
# Example usage/call, in the same file
#
if __name__ == "__main__":
    # Hard-coded example usage
    input_file = "data/PVH_resources.json"    # This is the JSON file containing the array of HTML strings
    output_file = "output_results.json"   # We'll write the results here

    # The same 'equity_ticker', 'geography', and 'periodicity' for all snippets in the file
    ticker = "COOL"
    geo = "US"
    period = "periodic_event"

    output_event_JSON_to_file(
        input_json_file=input_file,
        output_json_file=output_file,
        equity_ticker=ticker,
        geography=geo,
        periodicity=period
    )