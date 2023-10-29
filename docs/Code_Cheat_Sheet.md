# Code Cheat Sheet

## Python

### FAST API

#### Generate Openapi.yaml from Endpoints

```python
# requirments.txt
# PyYAML==6.0.1

app = FastAPI(
    title="TITLE",
    description="DESCRIPTION",
    version="1.0.0",
    openapi_tags=[{
        "name": "tag_name",
        "description": "tag_description",
    }],
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local server"}],
)

import yaml

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    openapi_schema = app.openapi()

    # Konvertieren der 'AnyUrl'-Objekte in Strings
    if "servers" in openapi_schema:
        for server in openapi_schema["servers"]:
            if hasattr(server["url"], "__str__"):  # Prüfen, ob das Objekt in einen String umgewandelt werden kann
                server["url"] = server["url"].__str__()

    order = ['openapi', 'info', 'servers', 'paths', 'components']

    yaml_output = ""
    for key in order:
        if key in openapi_schema:
            section = {key: openapi_schema[key]}
            yaml_output += yaml.dump(section, sort_keys=False)  # sort_keys=False behält die Reihenfolge der Schlüssel bei

    return Response(yaml_output, media_type="text/yaml")
```