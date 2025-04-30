import json
import os


def process_json_files(file_paths):
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"Skipped (file not found): {file_path}")
            continue

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        initial_event_count = len(data)
        initial_data_count = sum(len(event['data']) for event in data)

        cleaned_data = []
        removed_data_count = 0

        for event in data:
            original_data_length = len(event['data'])
            event['data'] = [
                d for d in event['data']
                if not d['file_name'].lower().endswith(('.html', '.htm'))
            ]
            removed_data_count += original_data_length - len(event['data'])

            if event['data']:
                cleaned_data.append(event)

        removed_event_count = initial_event_count - len(cleaned_data)

        if cleaned_data:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(cleaned_data, file, indent=2, ensure_ascii=False)
            print(f"Processed {file_path}: Removed {removed_event_count} events and {removed_data_count} data objects.")
        else:
            os.remove(file_path)
            print(f"Removed empty file after cleaning: {file_path}")

# Example usage
file_paths = [
    'Completed/JSONS/PVH_news.json',
    'Completed/JSONS/PVH_press.json',
    'Completed/JSONS/PVH_resources.json',
    'Completed/JSONS/CRDA_news.json',
    'Completed/JSONS/DSFIR_news.json',
    'Completed/JSONS/GIVN_news.json',
    'Completed/JSONS/GIVN_media_releases.json',
    'Completed/JSONS/GIVN_publication.json',
    'Completed/JSONS/GIVN_media.json',
    'Completed/JSONS/IFF_presentations.json',
    'Completed/JSONS/IFF_press.json',
    'Completed/JSONS/KO_poclicies-practices-reports.json',
    'Completed/JSONS/RL_newsroom.json',
    'Completed/JSONS/RL_news.json',
    'Completed/JSONS/RL_earnings.json',
    'Completed/JSONS/RL_presentations.json',
    'Completed/JSONS/SY1_news.json',
    'Completed/JSONS/SY1_financial.json',
    'Completed/JSONS/WDAY_press.json',
    'Completed/JSONS/WMT_news.json',
    'Completed/JSONS/WMT_events.json',
    'Completed/JSONS/KER_press.json',
    'Completed/JSONS/RMS_publications.json',
    'Completed/JSONS/RMS_policies-publications.json',
    'Completed/JSONS/MOWI_reports.json',
    'Completed/JSONS/MOWI_presentations.json',
    'Completed/JSONS/MOWI_capital-markets-day.json',
    'Completed/JSONS/SAP_events.json',
    'Completed/JSONS/WISE_reports.json',
    'Completed/JSONS/WISE_news.json',
    'Completed/JSONS/WISE_presentations.json',
    'Completed/JSONS/WISE_press.json',
    'Completed/JSONS/DGE_news.json',
    'Completed/JSONS/DGE_results.json',
    'Completed/JSONS/DGE_reports.json',
    'Completed/JSONS/DGE_press_releases.json',
    'Completed/JSONS/HEIO_media-releases.json',
    'Completed/JSONS/HEIO_reports.json',
    'Completed/JSONS/RB_investor_seminars.json',
    'Completed/JSONS/RB_agm.json',
    'Completed/JSONS/OR_news.json',
    'Completed/JSONS/OR_half.json',
    'Completed/JSONS/NOVO-B_finance.json',
    'Completed/JSONS/NOVO-B_news.json',
    'Completed/JSONS/SIE_press.json',
    'Completed/JSONS/RACE_press.json',
    'Completed/JSONS/RACE_financial.json',
    'Completed/JSONS/RACE_news.json',
    'Completed/JSONS/SAN_stock-exchange.json',
]
process_json_files(file_paths)
