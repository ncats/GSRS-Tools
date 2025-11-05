
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

def uniis_from_xml_bytes(data: bytes):
    #	-> set[str]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return set()
    uniis = set()
    for p in (
        ".//hl7:ingredient//hl7:ingredientSubstance//hl7:code",
        ".//hl7:ingredient//hl7:activeMoiety//hl7:code",
        ".//hl7:ingredient//hl7:ingredientSubstance//hl7:asEquivalentSubstance//hl7:code",
    ):
        for el in root.findall(p, HL7):
            c = el.get("code")
            if c: uniis.add(c)
    return uniis

def gather_uniis(input_path: str):
    # -> set[str]:
    all_uniis = set()

    for root, _, files in os.walk(input_path):
        for fname in files:
            print (fname)
            fpath = os.path.join(root, fname)
            fnl = fname.lower()

            # Direct XML
            if fnl.endswith(".xml"):
                try:
                    with open(fpath, "rb") as f:
                        all_uniis |= uniis_from_xml_bytes(f.read())
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
                                        all_uniis |= uniis_from_xml_bytes(zf_xml.read())
                                except Exception:
                                    pass
                except Exception:
                    pass

    return all_uniis

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input_folder> <output.csv>")
        sys.exit(1)

    input_folder, out_csv = sys.argv[1], sys.argv[2]
    uniis = sorted(gather_uniis(input_folder))

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["UNII"])
        for u in uniis:
            w.writerow([u])

    print(f"Wrote {len(uniis)} unique UNIIs to {out_csv}")

if __name__ == "__main__":
    main()

