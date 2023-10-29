import json

def is_sqlite(response_dict):
    return all(key in response_dict for key in ['database', 'rows', 'columns']) and \
           all(not isinstance(row, dict) for row in response_dict.get('rows', []))

def sqlite_to_dict(response_content):
    response_dict = json.loads(response_content)

    if not is_sqlite(response_dict):
        return response_dict

    columns = response_dict.get('columns', [])
    rows = response_dict.get('rows', [])

    formatted_data = [dict(zip(columns, row)) for row in rows]

    response_dict['rows'] = formatted_data

    return response_dict

def sqlite_to_json(response_content):
    response_dict = sqlite_to_dict(response_content)
    
    formatted_json = json.dumps(response_dict)

    return formatted_json
