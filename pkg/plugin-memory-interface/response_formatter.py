import json

def is_sqlite(response_dict):
    # Check if the response is from a SQLite instance
    return all(key in response_dict for key in ['database', 'rows', 'columns']) and \
           all(not isinstance(row, dict) for row in response_dict.get('rows', []))

def sqlite_to_dict(response_content):
    # Parse the JSON string into a Python dictionary
    response_dict = json.loads(response_content)

    # Check if the response is from a SQLite instance
    if not is_sqlite(response_dict):
        # If it's not, return the original response_dict
        return response_dict

    # Extract the column names and rows
    columns = response_dict.get('columns', [])
    rows = response_dict.get('rows', [])

    # Combine the column names and rows into a list of dictionaries
    formatted_data = [dict(zip(columns, row)) for row in rows]

    # Replace the 'rows' field in the original dictionary with the formatted data
    response_dict['rows'] = formatted_data

    return response_dict

def sqlite_to_json(response_content):
    # Convert the response_content to a dictionary
    response_dict = sqlite_to_dict(response_content)

    # Convert the dictionary back into a JSON string
    formatted_json = json.dumps(response_dict)

    return formatted_json
