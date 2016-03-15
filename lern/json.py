#!/usr/bin/python3
'''
This is meant to show general json handling in python.
'''
import json
# json is already basically a dictionary. 
json_string = '{"first_name": "Potato", "last_name": "Smasher"}'
# json.loads() just converts the json to a dictionary
parsed_json = json.loads(json_string)
print(parsed_json['first_name'])
"Potato"

# Convert a dict to json
dicky = {
      'first_name': 'Potato',
      'second_name': 'Smasher',
      'titles': ['Fireman', 'Deep fry'],
}
print(json.dumps(dicky))

