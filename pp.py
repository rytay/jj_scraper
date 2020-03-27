import json

with open('results.json' ,'r') as f:
    data=json.load(f)
    print(json.dumps(data,indent=1))