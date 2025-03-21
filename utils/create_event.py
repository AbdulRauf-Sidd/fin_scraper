def create_event(event_name, equity_ticker, geography, periodicity, data):
    # Validate the inputs for geography and periodicity to ensure they match expected values
    if geography not in ['US', 'European']:
        raise ValueError("Geography must be either 'US' or 'European'.")
    if periodicity not in ['periodic_event', 'non_periodic_event']:
        raise ValueError("Periodicity must be either 'periodic_event' or 'non_periodic_event'.")

    # Create the event metadata dictionary
    event_metadata = {
        "event_name": event_name,
        "equity_ticker": equity_ticker,
        "geography": geography,
        "periodicity": periodicity,
        "data": data  # 'data' is expected to be a list of event-related data
    }
    
    return event_metadata