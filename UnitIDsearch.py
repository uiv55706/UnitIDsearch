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

# Function to extract the station name from a folder name
def extract_station_name(folder_name):
    patterns = [
        r'_(\w+EVO)', 
        r'_(P\d+\w+)', 
        r'_(P\d+\w+\s)' 
    ]
    for pattern in patterns:
        match = re.search(pattern, folder_name)
        if match:
            return match.group(1)
    return folder_name

# Function to process the tracer files
def process_file(file_path, drive_name, search_terms):
    results = []
    try:
        with open(file_path, 'r') as file:
            parent_folder_name = os.path.basename(os.path.dirname(file_path))
            grandparent_folder_name = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            station_name = extract_station_name(grandparent_folder_name)
            lines = file.readlines()
            for i, line in enumerate(lines):
                for term in search_terms:
                    if term in line:
                        result_message = f"{drive_name} - {station_name}\n{line.strip()}\n"
                        if 'UNIT_RESULT' in line and i < len(lines) - 1:
                            next_line = lines[i + 1].strip()
                            result_message += f"{next_line}\n"
                        results.append(result_message)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
    return results


# Function to traverse directories and process tracer files within a date range
def traverse_directory(root_dir, drive_name, search_terms, start_date, end_date, station_name):
    results = []
    try:
        print(f"Processing drive: {drive_name} at path: {root_dir}")
        # Convert start_date and end_date to datetime.datetime objects
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if "tracer" in file.lower() and station_name.lower() in root.lower():  # Check if station name is in file path
                    file_path = os.path.join(root, file)
                    if 'old' in file_path.lower() or 'not_used' in file_path.lower() or 'not used' in file_path.lower():
                        print(f"Skipping file: {file_path}")
                        continue

                    # Check the file's modification date
                    file_mod_time = os.path.getmtime(file_path)
                    file_date = datetime.fromtimestamp(file_mod_time)
                    if start_datetime <= file_date <= end_datetime:
                        print(f"Processing file: {file_path}")
                        results.extend(process_file(file_path, drive_name, search_terms))
    except Exception as e:
        print(f"Error traversing directory {root_dir}: {e}")
    return results

# GUI function
def search_errors():
    search_terms = search_entry.get().split(',')  # Splitting multiple search terms
    if not search_terms:
        messagebox.showwarning("Input Error", "Please enter search terms.")
        return

    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()

    if start_date > end_date:
        messagebox.showwarning("Date Error", "End date must be greater than or equal to start date.")
        return

    station_name = station_entry.get()  # Get the station name entered by the user

    selected_drives = [drive for drive, var in drive_vars.items() if var.get()]

    results = []

    for drive_name in selected_drives:
        drive_path = production_pcs.get(drive_name)
        if drive_path:
            results.extend(traverse_directory(drive_path, drive_name, search_terms, start_date, end_date, station_name))
    
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
        messagebox.showinfo("Search Results", "No matching results found.")

def select_all():
    for var in drive_vars.values():
        var.set(True)

def unselect_all():
    for var in drive_vars.values():
        var.set(False)

def select_csv_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        # Read CSV file and set search terms
        try:
            df = pd.read_csv(file_path)
            search_entry.delete(0, tk.END)
            search_entry.insert(0, ','.join(df['search_terms']))
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading CSV file: {e}")

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

# Station name input
tk.Label(input_frame, text="Enter Station Name:", font=("Arial", 14)).pack(side=tk.LEFT)
station_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
station_entry.pack(side=tk.LEFT, padx=10)

# CSV file selection button
tk.Button(root, text="Select CSV File", command=select_csv_file, font=("Arial", 14)).pack(pady=5)

# Date inputs frame
date_frame = tk.Frame(root)
date_frame.pack(pady=10)

# Start date input
tk.Label(date_frame, text="Select Start Date:", font=("Arial", 14)).pack(side=tk.LEFT)
start_date_entry = DateEntry(date_frame, font=("Arial", 14), width=12, background='darkblue',
                             foreground='white', borderwidth=2, year=datetime.now().year)
start_date_entry.pack(side=tk.LEFT, padx=(10, 0))

# End date input
tk.Label(date_frame, text="Select End Date:", font=("Arial", 14)).pack(side=tk.LEFT, padx=(20, 0))
end_date_entry = DateEntry(date_frame, font=("Arial", 14), width=12, background='darkblue',
                           foreground='white', borderwidth=2, year=datetime.now().year)
end_date_entry.pack(side=tk.LEFT, padx=(10, 0))

# Select All and Unselect All buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Select All", command=select_all, font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Unselect All", command=unselect_all, font=("Arial", 14)).pack(side=tk.LEFT, padx=5)

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

# Search button
tk.Button(root, text="Search", command=search_errors, font=("Arial", 14)).pack(pady=20)

root.mainloop()