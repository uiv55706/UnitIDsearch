import json

# Load confiduration from config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    
output_path_uid = config['output_path_uids']
output_path_lines = config['output_path_lines']
production_pc_source = config['production_pc_path']
nr_of_columns = config['number_of_columns']