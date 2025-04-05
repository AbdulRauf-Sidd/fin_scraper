import os
import json

folder_path = 'Completed/JSONS/'

for file_name in os.listdir(folder_path):
    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(folder_path, file_name)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            events = json.load(f)

        # Filter out events with empty data lists
        original_count = len(events)
        filtered_events = [event for event in events if event.get("data")]

        if len(filtered_events) < original_count:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_events, f, indent=2)
            print(f"{file_name}: Removed {original_count - len(filtered_events)} empty event(s)")
        else:
            print(f"{file_name}: No empty events found")

    except Exception as e:
        print(f"Error processing {file_name}: {e}")
