from datetime import datetime

def convert_date_format(date_str):
    if date_str is None:
        return None
    
    try:
        # Parse the date from the given format (e.g., "Oct 17, 2024")
        parsed_date = datetime.strptime(date_str, "%b %d, %Y")
        # Convert it to the desired format (e.g., "2024/10/17")
        formatted_date = parsed_date.strftime("%Y/%m/%d")
        return formatted_date
    except ValueError:
        # If there's an error in parsing due to incorrect format
        return None

