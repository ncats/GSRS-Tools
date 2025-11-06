import os
import sys
import multiprocessing
import requests
import xml_parser_productlevel as xml_parser
import time
from datetime import datetime
import logging
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

logFilename = datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + '-uploader.log'

logging.basicConfig(filename=logFilename, level=logging.INFO)


def delete_one(url, i, headers):
    try:
        url2 = url + '/' + str(i)
        response = requests.delete(url2, headers=headers, verify=False)
        if (response.ok):
            logger.info(f"Deleted: {i}")
        else:
            logger.warning(f"Failed to delete id: {i}. Status Code: {response.status_code}")

    except Exception as e:
        logger.error(f"Exception occurred during delete of {i}: {e}")


def delete_range(url, firstId, lastId, headers):
    for number in range(firstId, lastId + 1):
        delete_one(url, number , headers)


def upload_data(filename, data, url, headers):
    try:
        response = requests.post(url, json=data, timeout=30, headers=headers, verify=False)
        if (response.ok):
            logger.info(f"Uploaded: {filename}")
        else:
            logger.warning(f"Failed to upload {filename}. Status Code: {response.status_code}")
    except Exception as e:
        logger.error(f"Exception occurred during upload of {filename}: {e}")

def upload_files_in_batches(data_list, batch_size, url, headers):
    logger.info("Starting batch upload of data...")

    # Create a pool of workers based on the number of CPU cores
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for i in range(0, len(data_list), batch_size):
            batch_data = data_list[i:i + batch_size]
            for index, data in enumerate(batch_data):
                try:
                    if data is not None:
                        filename = f"data_{i + index + 1}.json"
                        pool.apply_async(upload_data, args=(filename, data, url, headers))
                        # upload_data(filename, data, url, headers)
                    else:
                        logger.warning(f"Skipping upload for data index {i + index + 1} because it is None")
                except Exception as e:
                    logger.error(f"Exception occurred while preparing upload for data index {i + index + 1}: {e}")
        pool.close()
        pool.join()

    logger.info("Completed batch upload.")

def upload_files(data_zip_path, batch_size, url, headers):
    try:
        parsed_data = xml_parser.load_data_from_zip(data_zip_path)
        if not parsed_data:
            logger.error("No data available to upload. Please check the data.zip file.")
        else:
            # Upload data in batches
            upload_files_in_batches(parsed_data, batch_size, url, headers)
    except Exception as e:
        logger.error(f"An error occurred in the main upload process: {e}")



if __name__ == "__main__":

    # ===  common config info / begin   

    # In this script, you only need to worry about these 
    # values if you are setting useAutoload to True. 
    # You are better off using the uploader.py script instead.

    _debug=debug=os.environ.get('DEBUG')
    if (_debug==None): 
      _debug='FALSE' 
    debug=False
    if (_debug.upper()=='TRUE'):
       debug=True
    request_method=os.environ.get('REQUEST_METHOD')
    if (request_method==None): 
       request_method='POST'

    auth_username=os.environ.get('AUTH_USERNAME')
    auth_password=os.environ.get('AUTH_PASSWORD') 
    auth_key=os.environ.get('AUTH_KEY')
    auth_method=os.environ.get('AUTH_METHOD')
    auth_credential=''
    if (auth_method=='password'): 
       auth_credential={'auth-password': auth_password}
    if (auth_method=='key'): 
       auth_credential={'auth-key': auth_key}
    target_url=os.environ.get('TARGET_URL')
    headers={'auth-username': auth_username, 'content-type': 'application/json'} 
    headers.update(auth_credential)
    config_vars = 'debug request_method auth_username auth_password auth_key auth_method target_url' 

    if(debug): 
      print("=== Config vars ===") 
      for var in config_vars.split(" "): 
        print ("{}: {}".format(var,  str(locals()[var])))
      print("===")

    # ===  common config info / end   

    # Handle input folder and output zipfile path

    print(len(sys.argv))

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input_json_zipfile_path>")
        print(f"\nExample: python3 \$code/uploader.py processed-json-zip/all_dailymed_human_rx-jsons.zip")
        sys.exit(1)

    input_json_zipfile_path = sys.argv[1]

    batch_size = 50
    _headers = headers
    _url = target_url
    data_zip_path = input_json_zipfile_path

    # firstId, LastId; one is added to last id to make it work right ... make this cleaner
    # delete_range(urlPROD, 21, 170, headersPROD)
    # delete_one(urlPROD, 14917, headersPROD)

    upload_files(data_zip_path, batch_size, _url, _headers)


