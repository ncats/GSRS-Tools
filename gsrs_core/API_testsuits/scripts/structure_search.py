import requests
import json
import csv
from sample_headers import headerspost


csv_file_path = 'data_elements.csv'
base_url = "https://gsrs-uat.preprod.fda.gov/api/v1/substances/interpretStructure"
base_url2 = "https://gsrs-uat.preprod.fda.gov/api/v1/substances/structureSearch"
with open(csv_file_path, mode='r') as file:
    csv_reader = csv.DictReader(file)      
    for index, row in enumerate(csv_reader, start=1):
        data = row['smiles']
        query_params1 = {}
        response = requests.post(base_url, headers=headerspost, params=query_params1, data=data, verify=False)        
        if response.status_code == 200:
            print(data, f"Request {index} was successful!")
            response_dict = json.loads(response.text)
            structure = response_dict.get("structure")
            if structure:
                ida = structure.get('id')
                print(f"ID for request {index}: {ida}")
            else:
                print(f"No structure found for request {index}")
        else:
            print(f"Error {index}:", response.status_code, response.text)
            continue  
        query_params = {
            "q": ida,
            "type": "structuresearch",
            "smiles": data
        }
        response1 = requests.get(base_url2, headers=headerspost, params=query_params, data=data, verify=False)
        
        if response1.status_code == 200:
            print(f"Request {index} (GET) was successful!", data)
            response1_dict = json.loads(response1.text)
            print(type(response1_dict), response1_dict['finished'])
            print(f"Response1 for request {index}: {response1_dict}")
        else:
            print(f"Error {index} (GET):", response1.status_code, response1.text)

print("All requests completed.")