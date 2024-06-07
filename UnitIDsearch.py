import os
import pandas as pd
import re
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, time
from tkcalendar import DateEntry

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
        print(f"Extracting station name from folder: {station_folder}")  # Debugging print
        match = re.search(r'P(.*)', station_folder)
        if match:
            station_name = match.group(1)
            print(f"Extracted station name: {station_name}")  # Debugging print
            return station_name
    print("Logs folder not found in path.")  # Debugging print
    return "Unknown Station"

# Function to process the tracer files
def process_file(file_path, drive_name, search_terms, found_terms):
    results = []
    try:
        with open(file_path, 'r') as file:
            station_name = extract_station_name_from_logs(file_path)
            lines = file.readlines()
            for i, line in enumerate(lines):
                for term in search_terms:
                    if term in line:
                        found_terms.add(term)
                        result_message = f"{drive_name} - {station_name}\n{line.strip()}\n"
                        if 'UNIT_RESULT' in line and i < len(lines) - 1:
                            next_line = lines[i + 1].strip()
                            result_message += f"{next_line}\n"
                        results.append(result_message)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return results

# Function to traverse directories and process tracer files within a date range
def traverse_directory(root_dir, drive_name, search_terms, start_date, end_date, station_name, found_terms):
    results = []
    try:
        print(f"Processing drive: {drive_name} at path: {root_dir}")
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if "tracer" in file.lower() and station_name.lower() in root.lower():
                    file_path = os.path.join(root, file)
                    print(f"Found file: {file_path}")  # Debugging print
                    if 'old' in file_path.lower() or 'not_used' in file_path.lower() or 'not used' in file_path.lower():
                        print(f"Skipping file: {file_path}")
                        continue

                    file_mod_time = os.path.getmtime(file_path)
                    file_date = datetime.fromtimestamp(file_mod_time)
                    if start_datetime <= file_date <= end_datetime:
                        print(f"Processing file: {file_path}")
                        results.extend(process_file(file_path, drive_name, search_terms, found_terms))
    except Exception as e:
        print(f"Error traversing directory {root_dir}: {e}")
    return results

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

    # Get selected drives from the checkboxes
    selected_drives = [drive for drive, var in drive_vars.items() if var.get()]

    results = []
    found_terms = set()

    for drive_name in selected_drives:
        drive_path = production_pcs.get(drive_name)
        if drive_path:
            drive_results = traverse_directory_uids(drive_path, drive_name, search_terms, start_date, end_date, station_name, found_terms)
            results.extend(drive_results)

    not_found = set(search_terms) - found_terms
    if results:
        output_file_path = r'\\vt1.vitesco.com\SMT\didt1083\01_MES_PUBLIC\1.6.Production Errors\output_uids.txt'
        try:
            with open(output_file_path, 'w') as output_file:
                for result in results:
                    output_file.write(result + "\n")
            messagebox.showinfo("Search Results", f"Results written to {output_file_path}")
        except Exception as e:
            messagebox.showerror("File Error", f"Could not write to file: {e}")
    else:
        if not_found:
            messagebox.showinfo("Search Results", f"No matching results found for terms: {', '.join(not_found)}")
        else:
            messagebox.showinfo("Search Results", "No matching results found.")

# Function to process files and extract UID details
def process_file_uids(file_path, drive_name, search_terms, found_terms):
    results = []
    try:
        with open(file_path, 'r') as file:
            station_name = extract_station_name_from_logs(file_path)
            lines = file.readlines()
            for i, line in enumerate(lines):
                for term in search_terms:
                    if term in line:
                        found_terms.add(term)
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

# Function to traverse directories and process files for UID extraction within a date range
def traverse_directory_uids(root_dir, drive_name, search_terms, start_date, end_date, station_name, found_terms):
    results = []
    try:
        print(f"Processing drive: {drive_name} at path: {root_dir}")
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if "tracer" in file.lower() and station_name.lower() in root.lower():
                    file_path = os.path.join(root, file)
                    print(f"Found file: {file_path}")  # Debugging print
                    if 'old' in file_path.lower() or 'not_used' in file_path.lower() or 'not used' in file_path.lower():
                        print(f"Skipping file: {file_path}")
                        continue

                    file_mod_time = os.path.getmtime(file_path)
                    file_date = datetime.fromtimestamp(file_mod_time)
                    if start_datetime <= file_date <= end_datetime:
                        print(f"Processing file: {file_path}")
                        results.extend(process_file_uids(file_path, drive_name, search_terms, found_terms))
    except Exception as e:
        print(f"Error traversing directory {root_dir}: {e}")
    return results

# Function to handle the search errors functionality
def search_errors():
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

    results = []
    found_terms = set()

    for drive_name in selected_drives:
        drive_path = production_pcs.get(drive_name)
        if drive_path:
            drive_results = traverse_directory(drive_path, drive_name, search_terms, start_date, end_date, station_name, found_terms)
            results.extend(drive_results)

    not_found = set(search_terms) - found_terms
    if results:
        output_file_path = r'\\vt1.vitesco.com\SMT\didt1083\01_MES_PUBLIC\1.6.Production Errors\output.txt'
        try:
            with open(output_file_path, 'w') as output_file:
                for result in results:
                    output_file.write(result + "\n")
            messagebox.showinfo("Search Results", f"Results written to {output_file_path}")
        except Exception as e:
            messagebox.showerror("File Error", f"Could not write to file: {e}")
    else:
        if not_found:
            messagebox.showinfo("Search Results", f"No matching results found for terms: {', '.join(not_found)}")
        else:
            messagebox.showinfo("Search Results", "No matching results found.")

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
root.geometry("1280x720")

# Frame for search term and station name inputs
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# Search term input
tk.Label(input_frame, text="Enter Search Terms:", font=("Arial", 14)).pack(side=tk.LEFT)
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
date_frame.pack(pady=10, padx=10, anchor='w')

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

# Drive selection
production_pcs = read_production_pcs(r'\\vt1.vitesco.com\SMT\didt1083\01_MES_PUBLIC\1.6.Production Errors\production_pc.xlsx')

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
tk.Label(scrollable_frame, text="Select Production PC's:", font=("Arial", 14)).grid(row=0, column=0, columnspan=4, sticky='w', pady=10)

max_columns = 4  # Number of columns in the grid
current_row = 1
current_column = 0

for drive_name in production_pcs.keys():
    var = tk.BooleanVar()
    tk.Checkbutton(scrollable_frame, text=drive_name, variable=var, font=("Arial", 12)).grid(row=current_row, column=current_column, sticky='w', padx=10, pady=5)
    drive_vars[drive_name] = var
    current_column += 1
    if current_column >= max_columns:
        current_column = 0
        current_row += 1

# Search buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

tk.Button(button_frame, text="Search and output lines", command=search_errors, font=("Arial", 14)).pack(side=tk.LEFT, padx=10)
tk.Button(button_frame, text="Search and output UIDs", command=search_and_output_uids, font=("Arial", 14)).pack(side=tk.LEFT, padx=10)

root.mainloop()
