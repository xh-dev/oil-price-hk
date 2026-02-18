import json

data = open('price-info.json').read()
print(data)
json_data = json.loads(data)
