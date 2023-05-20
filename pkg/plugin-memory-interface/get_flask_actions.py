# get_flask_actions.py
import requests
import logging
import re

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

    logging.info(path)
    
    data = request.get_data()

    response = requests.request(
        method=request.method,
        url=f"{MEMORY_HOST}/{path}",
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        params=params, 
        data=data,
        allow_redirects=False)

    # Assume the response is not JSON and set response_content accordingly
    response_content = response.text

    headers = [('Transfer-Encoding', 'identity')]  # Disable chunked transfer encoding

    return response_content, response.status_code, headers
