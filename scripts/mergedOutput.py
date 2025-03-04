import json
import os

def merge_json_files(file_list, output_file):
    combined_data = []

    for file_name in file_list:
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                try:
                    # Load the JSON content and add it to the combined list
                    data = json.load(f)
                    if isinstance(data, list):  # If it's a list, add its items
                        combined_data.extend(data)
                    else:  # Otherwise, wrap it in a list and extend
                        combined_data.append(data)
                except json.JSONDecodeError as e:
                    print(f"Error reading {file_name}: {e}")
        else:
            print(f"File {file_name} does not exist.")

    # Write the combined data to the output file
    with open(output_file, 'w') as output_f:
        try:
            json.dump(combined_data, output_f, indent=4)
            print(f"Successfully merged files into {output_file}")
        except json.JSONDecodeError as e:
            print(f"Error writing to {output_file}: {e}")

# List of JSON files to be merged
json_files = ['data.json','sec_filings.json','financial_scrapper/cl_press.json','financial_scrapper/cocacola_sec_filings.json', 
              'financial_scrapper/colgate_sec_filings.json', 'financial_scrapper/crda_esg.json' , 'financial_scrapper/wday_events.json',
              'financial_scrapper/iff_presentations.json', 'financial_scrapper/crda_news.json', 'financial_scrapper/iff_press.json',
              'financial_scrapper/sec_filings.json', 'financial_scrapper/wday_press.json', 'financial_scrapper/sy1_events.json',
              'financial_scrapper/wday_quarterly.json',  'financial_scrapper/corz_finance.json', 'financial_scrapper/crda_sec.json',
              'financial_scrapper/sy1_news.json', 'financial_scrapper/wmt_esg.json', 'financial_scrapper/corz_presentation.json',
              'financial_scrapper/dsfir_news.json', 'financial_scrapper/nvda_news.json', 'financial_scrapper/sy1_sec.json', 
              'financial_scrapper/wmt_events.json', 'financial_scrapper/corz_presentation.json', 'financial_scrapper/dsfir_news.json',
              'financial_scrapper/nvda_news.json', 'financial_scrapper/sy1_sec.json', 'financial_scrapper/wmt_events.json', 
              'financial_scrapper/corz_press.json', 'financial_scrapper/dsm_press.json', 'financial_scrapper/nvda_press.json', 
              'financial_scrapper/wmt_news.json', 'financial_scrapper/cpb_events.json', 'financial_scrapper/givd_news.json', 
              'financial_scrapper/pinterest_events-and-presentations.json', 'financial_scrapper/wmt_quarterly.json', 
              'financial_scrapper/cpb_news.json', 'financial_scrapper/givd_sec.json', 'financial_scrapper/pinterest_press_releases.json',
              'financial_scrapper/unlv_presentations.json']

# Output file where the merged data will be saved
output_json = 'merged_output.json'

# Merge the files
merge_json_files(json_files, output_json)
