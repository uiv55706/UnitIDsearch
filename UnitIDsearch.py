import os
import pandas as pd
import re
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, time
from tkcalendar import DateEntry
import tempfile
import json
import logging
import sys
import csv

# Set up a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler('UnitID_Log.txt', mode='a')  # Append mode
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Define a log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Set the formatter for both handlers
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Redirect standard output to the logging system
class StreamToLogger:
    def __init__(self, logger, level=logging.INFO):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():  # Avoid logging empty messages
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass  # No need to flush for this example

# Redirect stdout to the logger
sys.stdout = StreamToLogger(logger, logging.INFO)  # Use logger instance
sys.stderr = StreamToLogger(logger, logging.ERROR)  # Optionally redirect stderr as well
# Load confiduration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    
output_path_uid = config['output_path_uids']
output_path_lines = config['output_path_lines']
production_pc_source = config['production_pc_path']
nr_of_columns = config['number_of_columns']

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
    # Correctly combine the regex pattern with re.IGNORECASE flag
    match = re.search(r'([^\\\/]+)[\\\/]Logs[\\\/]', file_path, re.IGNORECASE)
    print("First: ", match)
    if match:
        station_folder = match.group(1)
        match_station = re.search(r'^[^_]*_[^_]*_(.*)', station_folder)
        print("Second: ", match_station)
        if match_station:
            station_name = match_station.group(1)
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
                        # Testing with different sample paths
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return results

# Function to traverse directories and process tracer files within a date range
def traverse_directory(root_dir, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard):
    results = []
    try:
        print(f"Processing drive: {drive_name} at path: {root_dir}")
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        for root, dirs, files in os.walk(root_dir):
            for file in files:
                
                # Check for standard application logs
                if not is_non_standard:
                    # Match "VitescoAppMonitoringService.log." with date and version suffixes
                    if (file.lower().startswith("vitescoappmonitoringservice.log.") or 
                        file.lower().endswith("tracer.txt")) and station_name.lower() in root.lower():
                        
                        file_path = os.path.join(root, file)
                        
                        # Skip files with 'old', 'not_used', etc. in their names
                        if 'old' in file_path.lower() or 'not_used' in file_path.lower() or 'not used' in file_path.lower():
                            continue

                        # Check if the file modification time falls within the specified date range
                        file_mod_time = os.path.getmtime(file_path)
                        file_date = datetime.fromtimestamp(file_mod_time)
                        if start_datetime <= file_date <= end_datetime:
                            print(f"Processing file: {file_path}")
                            results.extend(process_file(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard))

                # Check for non-standard application logs
                else:
                    if (file.lower().startswith("logging") or file.lower().endswith(".log")) and station_name.lower() in root.lower():
                        
                        file_path = os.path.join(root, file)
                        
                        # Skip files with 'old', 'not_used', etc. in their names
                        if 'old' in file_path.lower() or 'not_used' in file_path.lower() or 'not used' in file_path.lower():
                            continue

                        # Check if the file modification time falls within the specified date range
                        file_mod_time = os.path.getmtime(file_path)
                        file_date = datetime.fromtimestamp(file_mod_time)
                        if start_datetime <= file_date <= end_datetime:
                            print(f"Processing file: {file_path}")
                            results.extend(process_file(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard))
                    
    except Exception as e:
        print(f"Error traversing directory {root_dir}: {e}")
    return results


# Function to hide the window
def hide_window():
    root.withdraw()
    
#Function to combine the search lines function with the hide window function to put them on a single button
def line_hide_combine():
    hide_window()
    search_lines()
    
#Function to combine the search uids function with the hide window function to put them on a single button
def uid_hide_combine():
    hide_window()
    search_and_output_uids()

# Function to unhide the main window
def unhide_window():
    root.deiconify()
    
import csv

# Function to handle the search and output UIDs functionality
def search_and_output_uids():
    # Get search terms from entry field
    search_terms = search_entry.get().split(',')
    if not search_terms:
        messagebox.showwarning("Input Error", "Please enter search terms.")
        return

    # Get start and end dates from DateEntry widgets
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()

    if start_date > end_date:
        messagebox.showwarning("Date Error", "End date must be greater than or equal to start date.")
        return

    # Get the station name from entry field
    station_name = station_entry.get()
    
    # Get the non-standard selection
    is_non_standard = non_standard_var.get()

    # Get selected drives from the checkboxes
    selected_drives = [drive for drive, var in drive_vars.items() if var.get()]

    results = []
    found_terms = set()
    
    # Fetch the number of subassemblies, default to 1
    try:
        n = int(subassy_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "The number of subassemblies must be a valid number.")
        return

    if n <= 0:
        messagebox.showwarning("Input Error", "There must be at least one subassembly.")
        return

    # Create a temporary file to store found terms
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file_path = temp_file.name

        for drive_name in selected_drives:
            drive_path = production_pcs.get(drive_name)
            if drive_path:
                drive_results = traverse_directory_uids(drive_path, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard, n)
                results.extend(drive_results)

    not_found = set(search_terms) - found_terms
    output_file_path = output_path_uid

    try:
        with open(output_file_path, 'w', newline='') as output_file:
            csv_writer = csv.writer(output_file)

            # Dynamically generate the header row based on n
            header = ['Drive Name', 'Station Name', 'UID In'] + [f'UID Assy {i + 1}' for i in range(n)]
            csv_writer.writerow(header)  # Write the header row

            if not results:
                messagebox.showinfo("Search Results", "No matching results found.")
                return

            # Iterate over results
            for result in results:
                if len(result) != n + 3:  # Ensure the result is the expected length
                    logger.warning(f"Unexpected result format: {result}")
                    continue

                drive_name = result[0]
                station_name = result[1]
                uid_in = result[2]
                uid_assy_list = result[3:n+3]

                if uid_in is None or any(assy is None for assy in uid_assy_list):
                    logger.warning(f"Incomplete UID data in result: {result}")
                    continue

                # Write the row with drive name, station name, UID In, and 'n' UID Assy values
                csv_writer.writerow([drive_name, station_name, uid_in] + uid_assy_list)

        messagebox.showinfo("Search Results", f"Results written to {output_file_path}")
        unhide_window()

    except Exception as e:
        messagebox.showerror("File Error", f"Could not write to file: {e}")
        unhide_window()

    # Delete the temporary file
    os.remove(temp_file_path)

# Function to process files and extract UID details based on dynamic uid_assy fields
def process_file_uids(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard, n):
    results = []

    # Retrieve value from subassy_entry and validate
    n = int(subassy_entry.get())  # Assuming subassy_entry is defined elsewhere
    if str(n) == '0':
        messagebox.showwarning("Input Error", "There must be at least one subassembly")
        return
    
    # Initialize a set to track processed uid groups
    processed_uid_groups = set()

    try:
        # Debugging file path before extracting station name
        print(f"Processing file path in process_file_uids: {file_path}")

        # Extract station name from the entry (assuming station_entry is defined elsewhere)
        station_name = station_entry.get()
        print(f"Extracted station name in process_file_uids: {station_name}")  # Debug

        with open(file_path, 'r') as file:
            station_name = station_entry.get()
            lines = file.readlines()
            for i, line in enumerate(lines):
                for term in search_terms:
                    if term in line:
                        found_terms.add(term)
                        temp_file.write(term + "\n")
                        
                        # Search for uid_in
                        uid_in_match = re.search(r'uid_in="([^"]+)"', line)
                        uid_in = uid_in_match.group(1) if uid_in_match else None
                        
                        # Search for uid_assy_1 to uid_assy_n
                        uid_assy_list = []
                        for j in range(1, n + 1):
                            uid_assy_match = re.search(f'uid_assy_{j}="([^"]+)"', line)
                            if uid_assy_match:
                                uid_assy_list.append(uid_assy_match.group(1))
                            else:
                                uid_assy_list.append('')  # Keep columns aligned
                        
                        # Create uid group tuple
                        uid_group = (uid_in, tuple(uid_assy_list))
                        
                        # Only append results if uid_in is found and this uid group hasn't been processed
                        if uid_in and uid_group not in processed_uid_groups:
                            print(file_path)
                            station_name = extract_station_name_from_logs(file_path)  # Assuming extract_station_name_from_logs is defined elsewhere
                            print(station_name)
                            # Append drive_name, station_name, uid_in, and uid_assy_list
                            result_message = [drive_name, station_name, uid_in] + uid_assy_list
                            results.append(result_message)
                            # Track processed uid group
                            processed_uid_groups.add(uid_group)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    
    return results

# Function to traverse directories and process files for UID extraction within a date range
def traverse_directory_uids(root_dir, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard, n):
    n = int(subassy_entry.get())
    results = []
    try:
        print(f"Processing drive: {drive_name} at path: {root_dir}")
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        for root, dirs, files in os.walk(root_dir):
            for file in files:

                # Check for standard application logs
                if not is_non_standard: 
                # Match "VitescoAppMonitoringService.log." with date and version suffixes
                    if (file.lower().startswith("vitescoappmonitoringservice.log.") or 
                        file.lower().endswith("tracer.txt")) and station_name.lower() in root.lower():

                        file_path = os.path.join(root, file)
                        
                        # Filter out 'old' and 'not_used' files
                        if 'old' in file_path.lower() or 'not_used' in file_path.lower():
                            continue
                        
                        # Verify date range
                        file_mod_time = os.path.getmtime(file_path)
                        file_date = datetime.fromtimestamp(file_mod_time)
                        if start_datetime <= file_date <= end_datetime:
                            print(f"Calling process_file_uids with file path: {file_path}")
                            results.extend(process_file_uids(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard, n))
                
                # Check for non-standard application logs
                else:
                    if (file.lower().startswith("logging") or file.lower().endswith(".log")) and station_name.lower() in root.lower():

                        file_path = os.path.join(root, file)
                        
                        # Filter out 'old' and 'not_used' files
                        if 'old' in file_path.lower() or 'not_used' in file_path.lower():
                            continue
                        
                        # Verify date range
                        file_mod_time = os.path.getmtime(file_path)
                        file_date = datetime.fromtimestamp(file_mod_time)
                        if start_datetime <= file_date <= end_datetime:
                            print(f"Calling process_file_uids with file path: {file_path}")
                            results.extend(process_file_uids(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard, n))

    except Exception as e:
        print(f"Error traversing directory {root_dir}: {e}")
    return results

# Function to handle the search lines functionality
def search_lines():
    # Get search terms from entry field
    search_terms = search_entry.get().split(',')
    if not search_terms:
        messagebox.showwarning("Input Error", "Please enter search terms.")
        return

    # Get start and end dates from DateEntry widgets
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()

    if start_date > end_date:
        messagebox.showwarning("Date Error", "End date must be greater than or equal to start date.")
        return

    # Get the station name from entry field
    station_name = station_entry.get()

    # Get selected drives from the checkboxes
    selected_drives = [drive for drive, var in drive_vars.items() if var.get()]
    
    # Get the non-standard selection
    is_non_standard = non_standard_var.get()

    results = []
    found_terms = set()

    # Create a temporary file to store found terms
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file_path = temp_file.name

        for drive_name in selected_drives:
            drive_path = production_pcs.get(drive_name)
            if drive_path:
                drive_results = traverse_directory(drive_path, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard)
                results.extend(drive_results)

    not_found = set(search_terms) - found_terms
    output_file_path = output_path_lines
    try:
        with open(output_file_path, 'w') as output_file:
            for result in results:
                output_file.write(result + "\n")
            if not_found:
                output_file.write(f"\nNot Found Search Terms: {', '.join(not_found)}\n")
        messagebox.showinfo("Search Results", f"Results written to {output_file_path}")
        unhide_window()
    except Exception as e:
        messagebox.showerror("File Error", f"Could not write to file: {e}")
        unhide_window()

    # Read the temporary file and compare with the original search terms
    try:
        with open(temp_file_path, 'r') as temp_file:
            found_terms_in_file = set(temp_file.read().splitlines())
        not_found_terms = set(search_terms) - found_terms_in_file
        if not_found_terms:
            messagebox.showinfo("Search Results", f"The following terms were not found: {', '.join(not_found_terms)}")
    except Exception as e:
        print(f"Error reading temporary file: {e}")

    # Delete the temporary file
    os.remove(temp_file_path)

# Function to select all checkboxes
def select_all():
    for var in drive_vars.values():
        var.set(True)

# Function to unselect all checkboxes
def unselect_all():
    for var in drive_vars.values():
        var.set(False)

# Function to allow user to select a CSV file containing search terms
def select_csv_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            df = pd.read_csv(file_path)
            search_entry.delete(0, tk.END)
            search_entry.insert(0, ','.join(df['search_terms']))
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading CSV file: {e}")

# Function to enable scrolling with mouse wheel
def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Setup the main window
root = tk.Tk()
root.title("Unit ID Search")
root.geometry("1720x820")

# Load icon image (adjust path to your icon file)
icon_path = "UnitIDsearch.ico"  # For .ico format
root.iconbitmap(icon_path)  # Set the window icon

# Frame for search term and station name inputs
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# Search term input
tk.Label(input_frame, text="Enter SN or other term to search for:", font=("Arial", 14)).pack(side=tk.LEFT)
search_entry = tk.Entry(input_frame, font=("Arial", 14), width=50)
search_entry.pack(side=tk.LEFT, padx=10)

# CSV file selection button
tk.Button(input_frame, text="Select CSV File", command=select_csv_file, font=("Arial", 14)).pack(side=tk.LEFT, padx=5)

# Station name input
tk.Label(input_frame, text="Enter Station Name:", font=("Arial", 14)).pack(side=tk.LEFT)
station_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
station_entry.pack(side=tk.LEFT, padx=10)

# Date inputs frame
date_frame = tk.Frame(root)
date_frame.pack(pady=10, padx=10)

# Start date input
tk.Label(date_frame, text="Select Start Date:", font=("Arial", 14)).pack(side=tk.LEFT)
start_date_entry = DateEntry(date_frame, font=("Arial", 14), width=12, background='darkblue',
                             foreground='white', borderwidth=2, year=datetime.now().year)
start_date_entry.pack(side=tk.LEFT, padx=(10, 20))

# End date input
tk.Label(date_frame, text="Select End Date:", font=("Arial", 14)).pack(side=tk.LEFT)
end_date_entry = DateEntry(date_frame, font=("Arial", 14), width=12, background='darkblue',
                           foreground='white', borderwidth=2, year=datetime.now().year)
end_date_entry.pack(side=tk.LEFT, padx=(10, 20))

# Select All button
select_all_btn = tk.Button(date_frame, text="Select All", command=select_all, font=("Arial", 14))
select_all_btn.pack(side=tk.LEFT, padx=(20, 5))

# Unselect All button
unselect_all_btn = tk.Button(date_frame, text="Unselect All", command=unselect_all, font=("Arial", 14))
unselect_all_btn.pack(side=tk.LEFT, padx=(20, 5))

# Checkbox for non-standard file types
non_standard_var = tk.BooleanVar()
non_standard_chk = tk.Checkbutton(date_frame, text="GHP Common", variable=non_standard_var, font=("Arial", 14))
non_standard_chk.pack(side=tk.LEFT, padx=(20, 5))

# Drive selection
production_pcs = read_production_pcs(production_pc_source)

drive_frame = tk.Frame(root)
drive_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas = tk.Canvas(drive_frame)
scrollbar = tk.Scrollbar(drive_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

scrollable_frame.bind_all("<MouseWheel>", on_mouse_wheel)

drive_vars = {}
tk.Label(scrollable_frame, text="Select Production Lines", font=("Arial", 14)).grid(row=0, column=0, columnspan=4, sticky='w', pady=10)

# Get and sort drive names alphabetically
sorted_drive_names = sorted(production_pcs.keys())

# Calculate the number of rows needed
num_drives = len(sorted_drive_names)
max_columns = nr_of_columns
num_rows = (num_drives + max_columns - 1) // max_columns

# Create checkboxes for each drive in column-major order
drive_vars = {}
for col in range(max_columns):
    for row in range(num_rows):
        index = col * num_rows + row
        if index < num_drives:
            drive_name = sorted_drive_names[index]
            var = tk.BooleanVar()
            tk.Checkbutton(scrollable_frame, text=drive_name, variable=var, font=("Arial", 12)).grid(row=row + 1, column=col, sticky='w', padx=10, pady=5)
            drive_vars[drive_name] = var

# Search buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

tk.Button(button_frame, text="Search and output lines", command=line_hide_combine, font=("Arial", 14)).pack(side=tk.LEFT, padx=10)
tk.Button(button_frame, text="Search and output SN Pairs", command=uid_hide_combine, font=("Arial", 14)).pack(side=tk.LEFT, padx=10)

# Number of subassemblies input
tk.Label(button_frame, text="Number of subassys", font=("Arial", 14)).pack(side=tk.RIGHT)
subassy_entry = tk.Entry(button_frame, font=("Arial", 14), width=2)
subassy_entry.pack(side=tk.RIGHT, padx=10)

# Set default text '1'
subassy_entry.insert(0, "1")
 
root.mainloop()
