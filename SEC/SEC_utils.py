import yaml

def load_sec_config(config_path: str = "config/SEC_config.yaml") -> list[dict]:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    equities = config.get('equities', [])
    required_keys = {"ticker", "edgar_url", "event_csv_path", "event_json_path"}

    for idx, equity in enumerate(equities):
        missing_keys = required_keys - equity.keys()
        if missing_keys:
            raise ValueError(f"Missing keys {missing_keys} in equity index {idx}: {equity}")

    return equities


equities = load_sec_config()
print(equities[0]['ticker'])  # AAPL
