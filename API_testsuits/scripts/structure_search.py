import requests
import json
headerspost={'auth-key':"xxxxxx",'auth-username':'xxxxxx', 'content-type': 'text/plain'}


base_url="https://gsrs-uat.preprod.fda.gov/api/v1/substances/interpretStructure"

query_params1={
}
data="CCCCCCCCC"
#data="CCOc1ccc(cc1)Cc2cc(ccc2Cl)[C@H]3[C@@H]([C@H]([C@@H]([C@@H](COC(=O)C)O3)OC(=O)C)OC(=O)C)O"    

response = requests.post(base_url, headers=headerspost,params=query_params1, data=data, verify=False)


if response.status_code == 200:
    print("Request was successful!")
    #print("Response:",response.text)
    response_dict = json.loads(response.text)
    #print("Response:", response_dict)
    structure=response_dict.get("structure")
    ida=structure.get('id')
    print(ida)
else:
    print("Error:", response.status_code, response.text)


base_url2 = "https://gsrs-uat.preprod.fda.gov/api/v1/substances/structureSearch"
query_params = {
    "q":ida,
    "type": "structuresearch",
    "smiles": data
}
print(type(query_params))
response1=requests.get(base_url2, headers=headerspost,params=query_params, data=data, verify=False)

if response1.status_code == 200:
    print("Request was successful!")
    print("Response:",response1.text)
    response1_dict = json.loads(response1.text)
    print("Response1:", response1_dict)

else:
    print("Error:", response1.status_code, response1.text)
