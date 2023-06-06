# get_flask_actions.py
import requests
import re
import json
from response_formatter import sqlite_to_dict

# Definiere die unterstützten Filter und Suchparameter
SUPPORTED_FILTERS = ['limit']
SUPPORTED_SEARCH = ['uuid']

def get_action(request, path, MEMORY_HOST):
    params = request.args.to_dict()
    filter_found = False
    search_found = False

    for param in params:
        # Wenn der Parameter unterstützt wird und der Pfad dem Muster entspricht
        if param in SUPPORTED_FILTERS and re.match(r'^.+/get_.+\.json$', path):
            filter_found = True
            # Teile den Pfad in drei Teile: Datenbankname, Ressourcenname und '.json'
            db_name, resource, json_ext = re.match(r'^(.+)/get_(.+)(\.json)$', path).groups()
            # Setze den neuen Pfad zusammen
            path = f'{db_name}/get_{resource}_with_{param}{json_ext}'
        if param in SUPPORTED_SEARCH and re.match(r'^.+/get_.+\.json$', path):
            if filter_found:
                # Ein Filterparameter wurde bereits gefunden, gib einen Fehler zurück
                return "error: search and filter parameters set. Only one can be provided at a time", 400, {}
            search_found = True
            # Teile den Pfad in drei Teile: Datenbankname, Ressourcenname und '.json'
            db_name, resource, json_ext = re.match(r'^(.+)/get_(.+)(\.json)$', path).groups()
            # Setze den neuen Pfad zusammen
            path = f'{db_name}/get_{resource}_by_{param}{json_ext}'
    
    data = request.get_data()

    response = requests.request(
        method=request.method,
        url=f"{MEMORY_HOST}/{path}",
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        params=params, 
        data=data,
        allow_redirects=False)


    # Use sqlite_to_dict to get a Python dictionary
    response_dict = sqlite_to_dict(response.text)

    # Check if 'rows' is a key in the dictionary
    if 'rows' in response_dict:
        # If it is, set response_content to the value of 'rows'
        response_content = json.dumps(response_dict['rows'])
    else:
        # If 'rows' is not a key in the dictionary, convert the entire dictionary back to a JSON string
        response_content = json.dumps(response_dict)

    headers = []

    return response_content, response.status_code, headers

