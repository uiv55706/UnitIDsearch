import os
from datetime import datetime, time
from file_manip import process_file, process_file_uids

# Function to traverse directories and process tracer files within a date range
def traverse_directory(root_dir, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard):
    results = []
    try:
        print(f"Processing drive: {drive_name} at path: {root_dir}")
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if ((is_non_standard and ("logging" in file.lower() or ".log" in file.lower())) or 
                    (not is_non_standard and "tracer.txt" in file.lower())) and station_name.lower() in root.lower():
                    file_path = os.path.join(root, file)
                    if 'old' in file_path.lower() or 'not_used' in file_path.lower() or 'not used' in file_path.lower():
                        continue

                    file_mod_time = os.path.getmtime(file_path)
                    file_date = datetime.fromtimestamp(file_mod_time)
                    if start_datetime <= file_date <= end_datetime:
                        print(f"Processing file: {file_path}")
                        results.extend(process_file(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard))
    except Exception as e:
        print(f"Error traversing directory {root_dir}: {e}")
    return results

# Function to traverse directories and process files for UID extraction within a date range
def traverse_directory_uids(root_dir, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard):
    results = []
    try:
        print(f"Processing drive: {drive_name} at path: {root_dir}")
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if ((is_non_standard and ("logging" in file.lower() or ".log" in file.lower())) or 
                    (not is_non_standard and "tracer.txt" in file.lower())) and station_name.lower() in root.lower():
                    file_path = os.path.join(root, file)
                    if 'old' in file_path.lower() or 'not_used' in file_path.lower() or 'not used' in file_path.lower():
                        continue

                    file_mod_time = os.path.getmtime(file_path)
                    file_date = datetime.fromtimestamp(file_mod_time)
                    if start_datetime <= file_date <= end_datetime:
                        print(f"Processing file: {file_path}")
                        results.extend(process_file_uids(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard))
    except Exception as e:
        print(f"Error traversing directory {root_dir}: {e}")
    return results