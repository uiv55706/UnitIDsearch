import pandas as pd
import re

# Function to read production PC names and paths from the Excel file
def read_production_pcs(file_path):
    production_pcs = {}
    try:
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            drive_name = row['drive_name']
            drive_path = row['drive_path']
            production_pcs[drive_name] = drive_path
    except Exception as e:
        print(f"Error reading Excel file: {e}")
    return production_pcs

# Function to extract the station name from the folder before the "Logs" folder
def extract_station_name_from_logs(file_path):
    match = re.search(r'([^\\\/]+)[\\\/]Logs[\\\/]', file_path)
    if match:
        station_folder = match.group(1)
        match = re.search(r'P(.*)', station_folder)
        if match:
            station_name = match.group(1)
            return station_name
    return "Unknown Station"

# Function to process the tracer files
def process_file(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard):
    results = []
    try:
        with open(file_path, 'r') as file:
            station_name = extract_station_name_from_logs(file_path)
            lines = file.readlines()
            for i, line in enumerate(lines):
                for term in search_terms:
                    if term in line:
                        found_terms.add(term)
                        temp_file.write(term + "\n")
                        result_message = f"{drive_name} - {station_name}\n{line.strip()}\n"
                        if 'UNIT_RESULT' in line and i < len(lines) - 1:
                            next_line = lines[i + 1].strip()
                            result_message += f"{next_line}\n"
                        results.append(result_message)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return results

# Function to process files and extract UID details
def process_file_uids(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard):
    results = []
    try:
        with open(file_path, 'r') as file:
            station_name = extract_station_name_from_logs(file_path)
            lines = file.readlines()
            for i, line in enumerate(lines):
                for term in search_terms:
                    if term in line:
                        found_terms.add(term)
                        temp_file.write(term + "\n")
                        uid_in_match = re.search(r'uid_in="([^"]+)"', line)
                        uid_assy_1_match = re.search(r'uid_assy_1="([^"]+)"', line)
                        if uid_in_match and uid_assy_1_match:
                            uid_in = uid_in_match.group(0)
                            uid_assy_1 = uid_assy_1_match.group(0)
                            result_message = f"{drive_name} - {station_name}\n{uid_in} {uid_assy_1}\n"
                            results.append(result_message)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return results