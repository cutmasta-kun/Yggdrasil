# Code Cheat Sheet

## Python

### FAST API

#### Generate Openapi.yaml from Endpoints

```python
# requirments.txt
# PyYAML==6.0.1


import yaml

@app.get("/openapi.yaml", include_in_schema=False) # `include_in_schema=False` for when the endpoint shouldn't be included in the docs
def get_openapi_yaml():
    openapi_schema = app.openapi()

    order = ['openapi', 'info', 'paths', 'components'] # Hardcode order of openapi.yaml. Makes it more readable for humans
    
    yaml_output = ""
    for key in order:
        section = {key: openapi_schema[key]}
        yaml_output += yaml.dump(section)
    
    return Response(yaml_output, media_type="text/yaml")
```