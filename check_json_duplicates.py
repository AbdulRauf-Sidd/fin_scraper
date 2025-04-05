import os
import json
from collections import defaultdict

# Folder containing the JSON files
folder_path = 'Completed/JSONS'

# Track repeated fields per file: {value: {filename: count}}
repeats = {
    "source_url": defaultdict(lambda: defaultdict(int)),
    "event_name": defaultdict(lambda: defaultdict(int)),
    "r2_url": defaultdict(lambda: defaultdict(int)),
}

# Traverse JSON files
for file_name in os.listdir(folder_path):
    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(folder_path, file_name)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Local counters to track repetitions within this file
            seen_source_url = defaultdict(int)
            seen_event_name = defaultdict(int)
            seen_r2_url = defaultdict(int)

            for event in data:
                event_name = event.get("event_name")
                if event_name:
                    seen_event_name[event_name] += 1

                for item in event.get("data", []):
                    source_url = item.get("source_url")
                    r2_url = item.get("r2_url")

                    if source_url:
                        seen_source_url[source_url] += 1
                    if r2_url:
                        seen_r2_url[r2_url] += 1

            # Store only duplicates
            for key, seen in [
                ("source_url", seen_source_url),
                ("event_name", seen_event_name),
                ("r2_url", seen_r2_url),
            ]:
                for val, count in seen.items():
                    if count > 1:
                        repeats[key][val][file_name] = count

    except Exception as e:
        print(f"Error reading {file_name}: {e}")

# Display the results
for field, values in repeats.items():
    if values:
        print(f"\nRepeated {field} values:\n" + "-" * 40)
        for val, files in values.items():
            print(f"{field}: {val}")
            for file, count in files.items():
                print(f"  -> File: {file}, Count: {count}")
            print()
    else:
        print(f"\nNo repeated {field} values found.")
