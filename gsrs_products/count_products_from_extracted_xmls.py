
#!/usr/bin/env python3
import os, sys, csv, zipfile
import xml.etree.ElementTree as ET
from typing import Set

HL7 = {"hl7": "urn:hl7-org:v3"}

def count_xml_files(input_path: str)  -> Set[str]:
    c = 0
    for root, _, files in os.walk(input_path):
        for fname in files:
            c = c + 1
    print (c)

def count_products_from_xml_bytes(data: bytes):
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return set()
    count=0 
    components_i=0
    for component in root.findall('.//hl7:component/hl7:section/hl7:subject', HL7):
        components_i=components_i+1
        products_i=0
        for manufacturedProduct in component.findall('./hl7:manufacturedProduct', HL7):
            products_i=products_i+1
            print ("loop ... component: " + str(components_i) + " ... product: " + str(products_i))
    return count 

def gather_product_counts(input_path: str):
    counts=0
    for root, _, files in os.walk(input_path):
        for fname in files:
            print (fname)
            fpath = os.path.join(root, fname)
            fnl = fname.lower()

            # Direct XML
            if fnl.endswith(".xml"):
                try:
                    with open(fpath, "rb") as f:
                        per_file_counts |= count_products_from_xml_bytes(f.read())
                        counts = per_file_counts + counts
                except Exception:
                    pass
                continue

            # ZIP containing XMLs
            if fnl.endswith(".zip"):
                try:
                    with zipfile.ZipFile(fpath, "r") as zf:
                        for name in zf.namelist():
                            if name.lower().endswith(".xml"):
                                try:
                                    with zf.open(name) as zf_xml:
                                        per_file_counts |= count_products_from_xml_bytes(zf_xml.read())
                                        counts = per_file_counts + counts
                                except Exception:
                                    pass
                except Exception:
                    pass

    return counts

def main():
    """
    cd $workspace
    python3 $code/gather_product_counts.py processed-xml 
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <input_folder>")
        sys.exit(1)

    input_folder, out_csv = sys.argv[1], sys.argv[2]
    total = gather_product_counts(input_folder)
    print(f"Total count: {total}")

if __name__ == "__main__":
    main()

