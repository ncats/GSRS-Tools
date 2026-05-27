import os
import sys
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import zipfile
import requests

"""
Set these values to pass credential and URL values  

export DEBUG=FALSE 
export REQUEST_METHOD=POST # or PUT
export AUTH_USERNAME=admin
export AUTH_METHOD=password # or key
export AUTH_PASSWORD=XXXXXX
export AUTH_KEY=XXXXXX
export TARGET_URL="http://localhost:8081/ginas/app/api/v1/products"
"""


# Load your CSV data if needed (Not currently used at FDA because we do UNII lookup automatically)
csv_file_path = 'Substance_UUID_UNII_Production.csv'

useDataDictionary = False

# deprecated
# useSubstanceKeyType='APPROVAL_ID'

# If you are uploading large amounts of data it is better to NOT use useAutoload 
# Instead, set to False and allow this script to write jsons to the filename set in variable output_zip, e.g. jsons.zip 
# Then, run the "uploader.py" script to upload using a threaded/async procedure.  
useAutoload = False

# HL7
HL7 = {'hl7': 'urn:hl7-org:v3'}


# To log issues

def log_to_file(log_file, message):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(message + '\n')

def safe_log(log_file_path, file_path, issue_type, message=""):
    if log_file_path and file_path:
        log_to_file(log_file_path, f"[{issue_type}] {file_path} | {message}")

# Date format for spl and making it for gsrs format

def get_date_mmddyyyy(value, log_file_path=None, file_path=None, issue_type="DATE_PARSE_ERROR"):
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%Y%m%d").strftime("%m/%d/%Y")
    except Exception as e:
        safe_log(log_file_path, file_path, issue_type, str(e))
        return ""

# Substance Details

def make_substance(ingredient_name, ingredient_type, substance_code, basis_code, numerator=None, denominator=None):
    return {
        'applicantIngredName': ingredient_name or '',
        'substanceKeyType': 'APPROVAL_ID',
        'ingredientType': ingredient_type or '',
        'substanceKey': substance_code or '',
        'basisOfStrengthSubstanceKey': basis_code or '',
        'basisOfStrengthSubstanceKeyType': 'APPROVAL_Id',
        'originalNumeratorNumber': numerator.get('value', '') if numerator is not None else '',
        'originalNumeratorUnit': numerator.get('unit', '').upper() if numerator is not None else '',
        'originalDenominatorNumber': denominator.get('value', '') if denominator is not None else '',
        'originalDenominatorUnit': denominator.get('unit', '').upper() if denominator is not None else ''
    }



# Construct at data dictionary from CSV to map UNII to UUID
# currently not in use
def csv_to_transformed_dict(csv_file, key_column, value_column):
    data_dict = {}
    with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        first_row = next(csv_reader)
        if key_column not in first_row or value_column not in first_row:
            print(f"Error: Column '{key_column}' or '{value_column}' not found in the CSV file.")
            return None
        file.seek(0)
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            try:
                key = row[key_column].strip()
                value = row[value_column].strip()
                data_dict[key] = value
            except KeyError as e:
                print(f"KeyError: {e}. Row data: {row}")
    return data_dict

# Main XML parser

def parse_xml_file(file_path, log_file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        GSRSProduct = {}
    except ET.ParseError as e:
        print('unable to parse')
        safe_log(log_file_path, file_path, "XML_PARSE_ERROR", str(e))
        return None
    except Exception as e:
        print('unable to open')
        safe_log(log_file_path, file_path, "XML_OPEN_ERROR", str(e))
        return None
    
    # Initialize dictionary to store extracted XML data
    try:
        XML_values = {}
        error = 0

        # Extract author information
        Author = {'RepresentativeOrgDUNS': '', 'RepresentativeOrg': ''}
        represented_org_element = root.find('.//hl7:author/hl7:assignedEntity/hl7:representedOrganization', HL7)

        try:
            Author['RepresentativeOrgDUNS'] = represented_org_element.find('.//hl7:id', HL7).attrib['extension'] if represented_org_element is not None and represented_org_element.find('.//hl7:id', HL7) is not None else ''
            Author['RepresentativeOrg'] = represented_org_element.find('.//hl7:name', HL7).text if represented_org_element is not None and represented_org_element.find('.//hl7:name', HL7) is not None else ''
        except Exception as e:
            Author['RepresentativeOrgDUNS'] = ''
            Author['RepresentativeOrg'] = ''
            safe_log(log_file_path, file_path, "AUTHOR_PARSE_ERROR", str(e))

        substring_to_remove = "LABEL"

        for component in root.findall('.//hl7:component/hl7:section/hl7:subject', HL7):

            for manufacturedProduct in component.findall('.//hl7:manufacturedProduct', HL7):

                XML_values = {
                    'routeAdmin': '',
                    'Ingredients': [],
                    'ActiveMoiety': [],
                    'SPLSHAPE': '',
                    'SPLSCORE': '',
                    'SPLSIZE': '',
                    'SPLIMPRINT': '',
                    'Application_ID': '',
                    'Application_Type': '',
                    'SPLCOLOR': '',
                    'RepresentativeOrgDUNS': Author['RepresentativeOrgDUNS'],
                    'RepresentativeOrg': Author['RepresentativeOrg'],
                    'marketingStatus': '',
                    'marketingdate_low': '',
                    'marketingdate_high': '',
                    'effective_time': ''
                }

                
                # Application, Marketing, Characteristics
                
                for subjectOf in manufacturedProduct.findall('.//hl7:subjectOf', HL7):

                    for approval in subjectOf.findall('.//hl7:approval', HL7):
                        try:
                            approval_code = approval.find('.//hl7:code', HL7)
                            approval_id = approval.find('.//hl7:id', HL7)

                            XML_values['Application_Type'] = approval_code.get('displayName', '') if approval_code is not None else ''
                            XML_values['Application_ID'] = approval_id.get('extension', '') if approval_id is not None else ''

                        except Exception as e:
                            safe_log(log_file_path, file_path, "APPLICATION_PARSE_ERROR", str(e))

                    for marketingAct in subjectOf.findall('.//hl7:marketingAct', HL7):
                        try:
                            marketingActstatus = marketingAct.find('.//hl7:statusCode', HL7)

                            if marketingActstatus is not None:
                                XML_values['marketingStatus'] = marketingActstatus.get('code', '')

                            low_el = marketingAct.find('.//hl7:low', HL7)
                            high_el = marketingAct.find('.//hl7:high', HL7)

                            low_val = low_el.get('value') if low_el is not None else ""
                            high_val = high_el.get('value') if high_el is not None else ""

                            XML_values['marketingdate_low'] = get_date_mmddyyyy(
                                low_val,
                                log_file_path,
                                file_path,
                                "MARKETING_LOW_PARSE_ERROR"
                            )

                            XML_values['marketingdate_high'] = get_date_mmddyyyy(
                                high_val,
                                log_file_path,
                                file_path,
                                "MARKETING_HIGH_PARSE_ERROR"
                            )

                        except Exception as e:
                            safe_log(log_file_path, file_path, "MARKETING_PARSE_ERROR", str(e))

                    for characteristic in subjectOf.findall('.//hl7:characteristic', HL7):
                        try:
                            char_code = characteristic.find('.//hl7:code', HL7)
                            char_value = characteristic.find('.//hl7:value', HL7)

                            if char_code is not None:
                                code_key = char_code.get('code', '')
                                value_text = ''

                                if char_value is not None:
                                    value_text = char_value.get('displayName', '') or char_value.get('value', '') or (char_value.text or '')

                                if code_key:
                                    XML_values[code_key] = value_text

                        except Exception as e:
                            safe_log(log_file_path, file_path, "CHARACTERISTIC_PARSE_ERROR", str(e))

                
                # Route of administration
                
                for consumedIn in manufacturedProduct.findall('.//hl7:consumedIn', HL7):
                    for substanceAdministration in consumedIn.findall('.//hl7:substanceAdministration', HL7):
                        try:
                            Administcode = substanceAdministration.find('.//hl7:routeCode', HL7) if substanceAdministration is not None else None
                            XML_values['routeAdmin'] = Administcode.get('displayName', '') if Administcode is not None else ''
                        except Exception as e:
                            safe_log(log_file_path, file_path, "ROUTE_PARSE_ERROR", str(e))

                
                # Choose file tags
                
                manufacturedDrug = manufacturedProduct.find('./hl7:manufacturedMedicine', HL7)

                if manufacturedDrug is None:
                    manufacturedDrug = manufacturedProduct.find('./hl7:manufacturedProduct', HL7)

                if manufacturedDrug is None:
                    manufacturedDrug = manufacturedProduct

                key = manufacturedDrug.find('.//hl7:code', HL7).get('code') if manufacturedDrug.find('.//hl7:code', HL7) is not None else 'na'

                XML_values['NDC Code_2 digits'] = key

                XML_values['ProductName'] = manufacturedDrug.find('.//hl7:name', HL7).text if manufacturedDrug.find('.//hl7:name', HL7) is not None else 'na'

                XML_values['DosageForm'] = manufacturedDrug.find('.//hl7:formCode', HL7).get('displayName') if manufacturedDrug.find('.//hl7:formCode', HL7) is not None else 'na'

                XML_values['Generic Name'] = 'na'
                for asEntityWithGeneric in manufacturedDrug.findall('.//hl7:asEntityWithGeneric', HL7):
                    generic_name_el = asEntityWithGeneric.find('.//hl7:name', HL7)
                    if generic_name_el is not None:
                        XML_values['Generic Name'] = generic_name_el.text

                
                # ActiveIngredient 
                
                for activeIngredient in manufacturedDrug.findall('.//hl7:activeIngredient', HL7):

                    quantity = activeIngredient.find('.//hl7:quantity', HL7)
                    ingredient_substance = activeIngredient.find('.//hl7:activeIngredientSubstance', HL7)

                    if ingredient_substance is None:
                        continue

                    name_el = ingredient_substance.find('.//hl7:name', HL7)
                    code_el = ingredient_substance.find('.//hl7:code', HL7)

                    substance_code = code_el.get('code', '') if code_el is not None else ''
                    basis_code = substance_code

                    active_moiety = ingredient_substance.find('.//hl7:activeMoiety/hl7:activeMoiety', HL7)

                    if active_moiety is not None:
                        moiety_code = active_moiety.find('.//hl7:code', HL7)
                        if moiety_code is not None:
                            basis_code = moiety_code.get('code', basis_code)

                    numerator = quantity.find('.//hl7:numerator', HL7) if quantity is not None else None
                    denominator = quantity.find('.//hl7:denominator', HL7) if quantity is not None else None

                    Substance = make_substance(
                        ingredient_name=name_el.text if name_el is not None else '',
                        ingredient_type='ACTIVE INGREDIENT',
                        substance_code=substance_code,
                        basis_code=basis_code,
                        numerator=numerator,
                        denominator=denominator
                    )

                    XML_values['Ingredients'].append(Substance)

                
                # Ingredient classCode 
                
                for ingredient in manufacturedDrug.findall('.//hl7:ingredient', HL7):

                    ingredient_substance = ingredient.find('.//hl7:ingredientSubstance', HL7)

                    if ingredient_substance is None:
                        continue

                    ingredientTypeXML = ingredient.get('classCode')

                    if ingredientTypeXML == 'ACTIB' or ingredientTypeXML == 'ACTIM' or ingredientTypeXML == 'ACTIR':
                        ingredientType = 'ACTIVE INGREDIENT'
                    else:
                        ingredientType = 'INACTIVE INGREDIENT'

                    quantity = ingredient.find('.//hl7:quantity', HL7)
                    name_el = ingredient_substance.find('.//hl7:name', HL7)
                    code_el = ingredient_substance.find('.//hl7:code', HL7)

                    substance_code = code_el.get('code', '') if code_el is not None else ''
                    basis_code = substance_code

                    active_moiety = ingredient.find('.//hl7:activeMoiety', HL7)

                    if ingredientTypeXML == 'ACTIM' and active_moiety is not None:
                        moiety_code = active_moiety.find('.//hl7:code', HL7)
                        if moiety_code is not None:
                            basis_code = moiety_code.get('code', basis_code)

                    else:
                        if ingredientTypeXML == 'ACTIR':
                            asEquivalentSubstance = ingredient_substance.find('.//hl7:asEquivalentSubstance', HL7)

                            if asEquivalentSubstance is not None:
                                asEquivalentSubstance_code = asEquivalentSubstance.find('.//hl7:code', HL7)

                                if asEquivalentSubstance_code is not None:
                                    basis_code = asEquivalentSubstance_code.get('code', basis_code)

                    numerator = quantity.find('.//hl7:numerator', HL7) if quantity is not None else None
                    denominator = quantity.find('.//hl7:denominator', HL7) if quantity is not None else None

                    Substance = make_substance(
                        ingredient_name=name_el.text if name_el is not None else '',
                        ingredient_type=ingredientType,
                        substance_code=substance_code,
                        basis_code=basis_code,
                        numerator=numerator,
                        denominator=denominator
                    )

                    XML_values['Ingredients'].append(Substance)

                
                # Root of xml version, set id etc.
                
                try:
                    log_message = f"{key, file_path}"
                    log_to_file(log_file_path, log_message)

                    doc_code = root.find('.//hl7:code', HL7)
                    doc_setid = root.find('.//hl7:setId', HL7)
                    doc_version = root.find('.//hl7:versionNumber', HL7)
                    doc_effective_time = root.find('.//hl7:effectiveTime', HL7)

                    XML_values['Product_Type'] = doc_code.get('displayName', '') if doc_code is not None else ''
                    XML_values['Set_Id'] = doc_setid.get('root', '') if doc_setid is not None else ''
                    XML_values['URL'] = 'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=' + XML_values['Set_Id'] if XML_values['Set_Id'] else ''
                    XML_values['version_number'] = doc_version.get('value', '') if doc_version is not None else ''

                    eff_val = doc_effective_time.get('value') if doc_effective_time is not None else ""
                    XML_values['effective_time'] = get_date_mmddyyyy(
                        eff_val,
                        log_file_path,
                        file_path,
                        "EFFECTIVE_TIME_PARSE_ERROR"
                    )

                except Exception as e:
                    safe_log(log_file_path, file_path, "ROOT_METADATA_PARSE_ERROR", str(e))

                
                # Packaging / asContent
                
                for asContent in component.findall('.//hl7:asContent', HL7):
                    try:
                        container_packaged_product = asContent.find('.//hl7:containerPackagedProduct', HL7)
                        if container_packaged_product is None:
                            container_packaged_product = asContent.find('.//hl7:containerPackagedMedicine', HL7)

                        form_code = container_packaged_product.find('.//hl7:formCode', HL7) if container_packaged_product is not None else None
                        quantity = asContent.find('.//hl7:quantity', HL7)
                        numerator = quantity.find('.//hl7:numerator', HL7) if quantity is not None else None
                        denominator = quantity.find('.//hl7:denominator', HL7) if quantity is not None else None

                        XML_values['formCode_Name'] = form_code.get('displayName', 'na') if form_code is not None else ''
                        XML_values['Package_Numerator'] = numerator.get('value', 'na') if numerator is not None else ''
                        XML_values['Package_Denominator'] = denominator.get('value', 'na') if denominator is not None else ''
                        XML_values['Package_NumeratorUnit'] = numerator.get('unit', 'na') if numerator is not None else ''
                        XML_values['Package_DenominatorUnit'] = denominator.get('unit', 'na') if denominator is not None else ''

                    except Exception as e:
                        safe_log(log_file_path, file_path, "PACKAGING_PARSE_ERROR", str(e))

                
                
                # Building GSRSProduct
                
                try:
                    GSRSProduct = {
                        "pharmacedicalDosageForm": XML_values.get('formCode_Name', '').upper(),
                        "routeAdmin": XML_values.get('routeAdmin', '').upper(),
                        "countryCode": "United States (USA)",
                        "language": "en",
                        "manufacturerName": XML_values.get('RepresentativeOrg', ''),
                        "manufacturerCode": XML_values.get('RepresentativeOrgDUNS', ''),
                        "manufacturerCodeType": "DUNS NUMBER",
                        "productProvenances": [
                            {
                                "productNames": [
                                    {
                                        "productName": XML_values.get('ProductName', ''),
                                        "displayName": True,
                                        "language": "en",
                                        "productNameType": "PRODUCT NAME"
                                    },
                                    {
                                        "productName": XML_values.get('Generic Name', ''),
                                        "displayName": False,
                                        "language": "en",
                                        "productNameType": "GENERIC NAME"
                                    }
                                ],
                                "productCodes": [
                                    {
                                        "productCode": key,
                                        "productCodeType": "NDC CODE"
                                    }
                                ],
                                "productCompanies": [
                                    {
                                        "productCompanyCodes": [
                                            {
                                                "companyCode": XML_values.get('RepresentativeOrgDUNS', ''),
                                                "companyCodeType": "DUNS NUMBER"
                                            }
                                        ],
                                        "provenanceDocumentId": XML_values.get('Set_Id', ''),
                                        "companyName": XML_values.get('RepresentativeOrg', '')
                                    }
                                ],
                                "productDocumentations": [
                                    {
                                        "documentId": XML_values.get('Set_Id', ''),
                                        "setIdVersion": XML_values.get('version_number', ''),
                                        "jurisdictions": "United States (USA)",
                                        "documentType": "SET ID"
                                    }
                                ],
                                "productIndications": [
                                    {
                                        "indicationsText": "All indication go here"
                                    }
                                ],
                                "provenance": "XML_SPL",
                                "productStatus": XML_values.get('marketingStatus', '').upper(),
                                "marketingStartDate": XML_values.get('marketingdate_low', ''),
                                "marketingEndDate": XML_values.get('marketingdate_high', ''),
                                "labelEffectiveDate": XML_values.get('effective_time', ''),
                                "productType": XML_values.get('Product_Type', '').upper().replace(substring_to_remove, ''),
                                "applicationType": XML_values.get('Application_Type', ''),
                                "applicationNumber": XML_values.get('Application_ID', ''),
                                "jurisdictions": "United States (USA)",
                                "productUrl": XML_values.get('URL', ''),
                                "publicDomain": "YES",
                                "isListed": "YES"
                            }
                        ],




                        "productManufactureItems": [
                            {
                                "productManufacturers": [
                                    {
                                        "manufacturerRole": "REPRESENTATIVE ORGANIZATION",
                                        "manufacturerName": XML_values.get('RepresentativeOrg', ''),
                                        "manufacturerCodeType": "DUNS NUMBER",
                                        "manufacturerCode": XML_values.get('RepresentativeOrgDUNS', '')
                                    }
                                ],
                                "productLots": [
                                    {
                                        "productIngredients": XML_values.get('Ingredients', [])
                                    }
                                ],
                                "dosageForm": XML_values.get('DosageForm', '').upper(),
                                "charNumFragments": XML_values.get('SPLIMPRINT', ''),
                                "charShape": XML_values.get('SPLSHAPE', '').upper(),
                                "charSize": XML_values.get('SPLSIZE', ''),
                                "charColor": XML_values.get('SPLCOLOR', '').upper(),
                                "routeOfAdministration": XML_values.get('routeAdmin', '').upper()
                            }
                       ]
                    }

                    # Assuming we only have on provenance.
                    # Clean up applicationNumber of non-useful values
                    tempRef=GSRSProduct['productProvenances'][0]
                    if tempRef['productType'] == "HUMAN PRESCRIPTION DRUG LABEL":
                        tempRef['applicationNumber'] = tempRef['applicationNumber'].replace(tempRef['applicationType'], "")


                except Exception as e:
                    print(f"[ERROR] Failed to create GSRSProduct. Error: {str(e)}")
                    safe_log(log_file_path, file_path, "GSRS_BUILD_ERROR", str(e))
                    GSRSProduct = {}

        log_message = f"[SUCCESS] parse XML file: {file_path}"
        log_to_file(log_file_path, log_message)

    except Exception as e:
        print('key', file_path)
        log_message = f"[ERROR] Failed to parse XML file: {file_path}. Error: {e}"
        log_to_file(log_file_path, log_message)
        GSRSProduct = {}

    return GSRSProduct

# Process multiple XML files

# The original way, reads xml files from single folder
def process_xml_files_list_dir(folder_path, log_file_path):
    xml_files = [filename for filename in os.listdir(folder_path) if filename.endswith(".xml")]
    parsed_data = []

    for filename in xml_files:
        file_path = os.path.join(folder_path, filename)
        parsed_data.append(parse_xml_file(file_path, log_file_path))
    return parsed_data

def find_all_xml_files_os_walk(folder_path):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(".xml"):
                file_paths.append(os.path.join(dirpath, filename))
    return file_paths


def process_xml_files_walk(folder_path, log_file_path):

    xml_files = find_all_xml_files_os_walk(folder_path)
    parsed_data = []
    for file_path in xml_files:
        parsed_data.append(parse_xml_file(file_path, log_file_path))
    return parsed_data


# Function to process multiple XML files
def process_xml_files(folder_path, log_file_path):
    if (xml_find_method == 'walk'):
        return process_xml_files_walk(folder_path, log_file_path)
    else:
        return process_xml_files_listdir(folder_path, log_file_path)	    

# Save parsed data as JSON files in a zip archive
def testing():
    print("Testing")




def save_data_as_zip(data_list, output_zip):
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for index, data in enumerate(data_list):
            if data:
                json_filename = f"data_{index + 1}.json"
                with zipf.open(json_filename, 'w') as json_file:
                    json_file.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

# Function to load data from a zip file containing JSON files
def load_data_from_zip(zip_file_path):
    data_list = []
    with zipfile.ZipFile(zip_file_path, 'r') as zipf:
        for file_name in zipf.namelist():
            if file_name.endswith(".json"):
                with zipf.open(file_name) as json_file:
                    data = json.load(json_file)
                    data_list.append(data)
    #print(f"[INFO] Loaded {len(data_list)} JSON files from the zip archive.")
    return data_list

# Entry point for XML parsing
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

    updateHeaders = headers
    updateUrl = target_url
    verifySsl = False

    # Handle input folder and output zipfile path

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_folder> <output_zipfile_path>")
        print(f"\nExample: python3 $code/xml_parser_productlevel.py  ./processed-xml/all_dailymed_human_rx processed-json-zip/all_dailymed_human_rx-jsons.zip")
        sys.exit(1)

    input_folder, output_zipfile_path = sys.argv[1], sys.argv[2]


    folder_path = input_folder
    output_zip = output_zipfile_path
    xml_find_method='walk'
    log_file_path = 'log.parser.txt'

    data_dictionary = { }
    # Not used now, maybe add later
    if (useDataDictionary):
        # Does this change, can we use useSubstanceKeyType value?, deprecated comment 
        key_column = 'UNII'  
        value_column = 'UUID'
        data_dictionary = csv_to_transformed_dict(csv_file_path, key_column, value_column)
    
    testing()

    # Process XML files and create zip archive with JSONs
    parsed_data = process_xml_files(folder_path, log_file_path)
    save_data_as_zip(parsed_data, output_zip)

    # Example of loading data from the created zip file
    # loaded_data = load_data_from_zip(output_zip)
