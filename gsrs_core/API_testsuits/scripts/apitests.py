import requests
import json
import time
import csv
from  test_config import headerspost, SERVER_URL, input_path, output_path, verify_flag
# Common base URL and headers
BASE_URL= SERVER_URL+"api/v1/substances"
input_file=input_path+"api_requests.csv"
output_file=output_path+"api_responses.csv"
def make_api_request(test_title, endpoint, headers_json, request_type="GET", data=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = json.loads(headers_json) if headers_json else {}
        #combined_headers = {**COMMON_HEADERS, **headers}
        start_time = time.time()

        if request_type == "POST" and data:
            data = json.dumps(data)  # Ensure the data is a properly formatted JSON string

        response = requests.request(method=request_type, url=url, headers=headerspost, data=data, verify=verify_flag)
        
        end_time = time.time()
        elapsed_time = end_time - start_time

        return {
            "Title": test_title,
            "URL": url,
            "Status Code": response.status_code,
            "Response Text": response.text,
            "Elapsed Time": elapsed_time
        }
    except Exception as e:
        return {
            "Title": test_title,
            "URL": url,
            "Status Code": "Error",
            "Response Text": str(e),
            "Elapsed Time": "N/A"
        }

def read_api_requests(filename):
    with open(filename, mode='r', newline='',encoding='utf-8', errors='ignore') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                print("Original JSON:", row['Data'])  # Debug print
                clean_json = ''.join(row['Data'].split())
                row['Data'] = json.loads(clean_json) if row['Data'] else None
                    
            except json.JSONDecodeError as e:
                print("Cleaned JSON:", clean_json)  # Debug print
                print(f"Error parsing JSON for row {row['Title']}: {e}")
                continue
            yield row


def write_to_csv(data, filename=output_file,encoding='utf-8', errors='ignore'):
    with open(filename, mode='w', newline='') as file:
        fieldnames = ['Title', 'URL', 'Status Code', 'Response Text', 'Elapsed Time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


request_configurations = read_api_requests(input_file)  ### read from api_requests.csv

# Execute requests and collect responses
responses = [
    make_api_request(
        config['Title'], config['Endpoint'], config['Headers'],
        config['Request Type'], config.get('Data')
    ) for config in request_configurations
]

# Write responses to CSV
write_to_csv(responses)
