# get_flask_actions.py
import re
import json
import logging
from response_formatter import sqlite_to_dict

logging.basicConfig(level=logging.INFO)

SUPPORTED_FILTERS = ['limit']
SUPPORTED_SEARCH = ['uuid']

# Regular Expression Konstanten
PATH_PATTERN = r'^.+/get_.+\.json$'
PATH_EXTRACT_PATTERN = r'^(.+)/get_(.+)(\.json)$'

def construct_path(db_name, resource, param, json_ext, is_search):
    """Konstruiert einen neuen Pfad basierend auf den gegebenen Parametern."""
    action = 'by' if is_search else 'with'
    return f'{db_name}/get_{resource}_{action}_{param}{json_ext}'

def determine_path(path, params):
    filter_found = False

    for param in params:
        # Wenn der Parameter unterstützt wird und der Pfad dem Muster entspricht
        if param in SUPPORTED_FILTERS and re.match(PATH_PATTERN, path):
            filter_found = True
            db_name, resource, json_ext = re.match(PATH_EXTRACT_PATTERN, path).groups()
            path = construct_path(db_name, resource, param, json_ext, False)
        elif param in SUPPORTED_SEARCH and re.match(PATH_PATTERN, path):
            if filter_found:
                raise ValueError("Both search and filter parameters set. Only one can be provided at a time.")
            db_name, resource, json_ext = re.match(PATH_EXTRACT_PATTERN, path).groups()
            path = construct_path(db_name, resource, param, json_ext, True)
    
    return path

def format_response_content(response_text):
    response_dict = sqlite_to_dict(response_text)

    if 'rows' in response_dict:
        return json.dumps(response_dict['rows'])
    else:
        return json.dumps(response_dict)
