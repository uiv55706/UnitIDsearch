import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, time
from tkcalendar import DateEntry
import tempfile
from config import output_path_uid, output_path_lines, production_pc_source, nr_of_columns
from file_manip import read_production_pcs
from gui import search_and_output_uids, search_lines, line_hide_combine, uid_hide_combine

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
non_standard_chk = tk.Checkbutton(date_frame, text="Non-standard Line", variable=non_standard_var, font=("Arial", 14))
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
tk.Label(scrollable_frame, text="Select Production PC's:", font=("Arial", 14)).grid(row=0, column=0, columnspan=4, sticky='w', pady=10)

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
tk.Button(button_frame, text="Search and output UIDs", command=uid_hide_combine, font=("Arial", 14)).pack(side=tk.LEFT, padx=10)

root.mainloop()
