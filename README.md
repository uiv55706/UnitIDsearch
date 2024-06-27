Unit ID Search Tool
Overview
The Unit ID Search Tool is a Python-based GUI application designed to facilitate the search and extraction of specific terms from production logs. The tool allows users to specify search terms, date ranges, and production PCs to scan for relevant logs and details. Results are saved to specified output files for further analysis.

Features
Search Terms Input: Enter search terms manually or load them from a CSV file.
Date Range Selection: Select start and end dates for filtering log files.
Station Name Input: Specify the station name to narrow down the search.
Drive Selection: Select production PCs from a list of available drives.
Non-standard Line Option: Toggle to search for non-standard log files.
Output Options: Search and output either matching lines or UID details.
Temporary File Handling: Temporary files are created to store intermediate search results.

Installation
Clone the repository:
git clone https://github.com/vladutlazar/UnitIDsearch
Navigate to the project directory:
cd unit-id-search-tool
Install required dependencies:
pip install -r requirements.txt

Configuration
Before running the tool, ensure the config.json file is correctly configured:

output_path_uids: Path to save the UID search results.
output_path_lines: Path to save the line search results.
production_pc_path: Path to the Excel file containing production PC names and paths.
Example config.json:

{
    "output_path_uids": "output_uids.txt",
    "output_path_lines": "output_lines.txt",
    "production_pc_path": "production_pcs.xlsx"
}

Usage
Run the application
Enter Search Terms: Manually or via CSV file.
Select Date Range: Using the date entry widgets.
Enter Station Name: To filter logs from a specific station.
Select Drives: Choose production PCs to scan for logs.
Non-standard Line Option: Check if you want to search non-standard logs.
Initiate Search: Click the button to search and output either lines or UIDs.

Functions
read_production_pcs(file_path): Reads production PC names and paths from an Excel file.
extract_station_name_from_logs(file_path): Extracts the station name from the log file path.
process_file(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard): Processes a log file to find search terms.
traverse_directory(root_dir, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard): Traverses directories to process files within a date range.
hide_window(): Hides the main window.
line_hide_combine(): Combines hiding window with search lines function.
uid_hide_combine(): Combines hiding window with search UIDs function.
unhide_window(): Unhides the main window.
search_and_output_uids(): Handles search and output for UIDs.
process_file_uids(file_path, drive_name, search_terms, found_terms, temp_file, is_non_standard): Processes a log file to extract UID details.
traverse_directory_uids(root_dir, drive_name, search_terms, start_date, end_date, station_name, found_terms, temp_file, is_non_standard): Traverses directories for UID extraction.
search_lines(): Handles search and output for lines.
select_all(): Selects all production PC checkboxes.
unselect_all(): Unselects all production PC checkboxes.
select_csv_file(): Allows user to select a CSV file containing search terms.
on_mouse_wheel(event): Enables scrolling with the mouse wheel.

License
This project is licensed under the MIT License. See the LICENSE file for details.
