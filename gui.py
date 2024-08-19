import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
import tempfile
import os
from datetime import datetime
from file_manip import read_production_pcs
from traversal import traverse_directory, traverse_directory_uids

# Function to hide the window
def hide_window(root):
    root.withdraw()

#Function to combine the search lines function with the hide window function to put them on a single button
def line_hide_combine(root, search_lines):
    hide_window(root)
    search_lines()
    
#Function to combine the search uids function with the hide window function to put them on a single button
def uid_hide_combine(root, search_and_output_uids):
    hide_window(root)
    search_and_output_uids()

# Function to unhide the main window
def unhide_window(root):
    root.deiconify()

# Function to handle the search and output UIDs functionality
def search_and_output_uids(search_entry, start_date_entry, end_date_entry, station_entry, drive_vars, production_pcs, output_path_uid, unhide_window, non_standard_var):
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

    # Create a temporary file to store found terms
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file_path = temp_file.name

        for drive_name in selected_drives:
            drive_path = production_pcs.get(drive_name)
            if drive_path:
                drive_results = traverse_directory_uids(drive_path, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard)
                results.extend(drive_results)

    not_found = set(search_terms) - found_terms
    if results:
        output_file_path = output_path_uid
        try:
            with open(output_file_path, 'w') as output_file:
                for result in results:
                    output_file.write(result + "\n")
            not_found_str = ", ".join(not_found) if not_found else "None"
            messagebox.showinfo("Search Complete", f"Search completed. Output written to {output_file_path}. Terms not found: {not_found_str}")
        except Exception as e:
            messagebox.showerror("File Error", f"Error writing to output file: {e}")
    else:
        messagebox.showinfo("No Results", "No matching results found.")
    unhide_window()

# Function to handle the search lines functionality
def search_lines(search_entry, start_date_entry, end_date_entry, station_entry, drive_vars, production_pcs, output_path_lines, unhide_window, non_standard_var):
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

    # Create a temporary file to store found terms
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file_path = temp_file.name

        for drive_name in selected_drives:
            drive_path = production_pcs.get(drive_name)
            if drive_path:
                drive_results = traverse_directory(drive_path, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard)
                results.extend(drive_results)

    not_found = set(search_terms) - found_terms
    if results:
        output_file_path = output_path_lines
        try:
            with open(output_file_path, 'w') as output_file:
                for result in results:
                    output_file.write(result + "\n")
            not_found_str = ", ".join(not_found) if not_found else "None"
            messagebox.showinfo("Search Complete", f"Search completed. Output written to {output_file_path}. Terms not found: {not_found_str}")
        except Exception as e:
            messagebox.showerror("File Error", f"Error writing to output file: {e}")
    else:
        messagebox.showinfo("No Results", "No matching results found.")
    unhide_window()
    
    
