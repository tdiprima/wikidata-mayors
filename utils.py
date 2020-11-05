import json
import time
from datetime import datetime

import pandas as pd
import requests


def convert_datatype(entry):
    if 'datatype' in entry:
        if entry['datatype'] == 'http://www.w3.org/2001/XMLSchema#decimal':
            return float(entry['value'])
        elif entry['datatype'] == 'http://www.w3.org/2001/XMLSchema#integer':
            return int(entry['value'])
        elif entry['datatype'] == 'http://www.w3.org/2001/XMLSchema#dateTime':
            date = entry['value']
            date = None if date.startswith('t') else datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            return date
    return entry['value']

def sleepy(r):
    print('status code:', r.status_code, r.reason)
    print('Sleeping... (1 minute)')
    time.sleep(60)


def wikidata_query(query):
    url = 'https://query.wikidata.org/sparql'
    # try:
    r = requests.get(url, params={'format': 'json', 'query': query})
    if r.status_code != 200:
        sleepy(r)
    else:
        try:
            data = r.json()
        except Exception as ex:
            print(ex)
            sleepy(r)
        # except json.JSONDecodeError as e:
        #     raise Exception('Invalid query')

        if ('results' in data) and ('bindings' in data['results']):
            columns = data['head']['vars']
            rows = []
            for binding in data['results']['bindings']:
                row = [convert_datatype(binding[col]) if col in binding else None
                   for col in columns]
                rows.append(row)
        else:
            raise Exception('No results')

        return pd.DataFrame(rows, columns=columns)
