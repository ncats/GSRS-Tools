# SD File Validator - User Guide

**Version 2.1**
**Last Updated: June 2026**
**Author: Marlene Kim, FDA GSRS**
**Author of JSChemify: Tyler Peryea, FDA GSRS**

**U.S. Food and Drug Administration**
**Global Substance Registration System**

*Disclaimer: The mention of commercial products, their sources, or their use in connection with material reported herein is not to be construed as either an actual or implied endorsement of such products by the Department of Health and Human Services or the Food and Drug Administration. Using this tool does not guarantee that your submission nor SD File will pass eCTD validation. It does not guarantee approval of your submission either. This validator is provided as a tool to assist with SD File preparation and does not replace official FDA guidance. The validation results are advisory and do not constitute an official FDA review.*

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Background](#2-background)
3. [System Requirements](#3-system-requirements)
4. [Setup Instructions](#4-setup-instructions)
5. [How to Use the SD File Validator](#5-how-to-use-the-sd-file-validator)
6. [Understanding Validation Results](#6-understanding-validation-results)
7. [Common Errors and Warnings Explained](#7-common-errors-and-warnings-explained)
8. [Troubleshooting](#8-troubleshooting)
9. [Support and Resources](#9-support-and-resources)
10. [Frequently Asked Questions (FAQ)](#10-frequently-asked-questions-faq)
11. [Appendix: Key SD File Requirements](#11-appendix-key-sd-file-requirements)

---

## 1. Introduction

The SD File Validator is a standalone, browser-based tool created to assist the public in validating Structure-Data Files (SD Files) intended for accompanying regulatory submissions to the FDA. This tool checks SD Files against the recommendations described in the GSRS Quick Guide to Creating a Structure-Data File (SD File) for Electronic Common Technical Document (eCTD) Submissions, helping to identify potential formatting and data issues that could lead to an Information Request (IR). Please note that the validator cannot capture all issues.

### Purpose

The primary purpose of the validator is to promote a more efficient assessment process by ensuring that:
- SD Files are formatted correctly according to V2000 standards.
- Required data fields are present and correctly named.
- Chemical structures are correctly represented and rendered.
- Common data quality issues are flagged for your review.

### Key Features

- **Client-Side Processing**: Runs directly in your web browser. No data is ever uploaded to a server, ensuring the confidentiality of your information.
- **Fully Self-Contained**: The tool is a single HTML file with no external dependencies. No companion files are required.
- **Offline Capable**: Works without an internet connection once the file is downloaded.
- **Visual Structure Display**: Renders chemical structures from MOL blocks for instant visual verification.
- **Comprehensive Validation**: Checks against a robust set of rules based on SD File Quick Guide.
- **Grouped and Detailed Reporting**: Generates a clear, downloadable report with grouped messages for easier review.

---

## 2. Background

### What is an SD File?

An SD File (Structure-Data File) is a standard file format used to store chemical structure information alongside associated data. Each record in an SD File typically contains a MOL file block, which describes a single chemical structure, followed by data fields (e.g., Name, CAS, Role).

- **File extension**: `.sdf` or `.txt`.
- **Structure Format**: The validator is designed **exclusively for the V2000 MOL format**. It will generate an error if it detects the V3000 format.
- **Record Delimiter**: Individual chemical records are separated by a line containing four dollar signs (`$$$$`).

### What to Include in an SD File

As per the GSRS Quick Guide to Creating a Structure-Data File (SD File) for Electronic Common Technical Document (eCTD) Submissions, SD Files should be used to represent the following types of substances:
- Drug substances
- Starting materials
- Intermediates
- Impurities
- Degradants
- Leachables exceeding the Analytical Evaluation Threshold (AET)

**Reagents and solvents should be excluded.**

### Recommended Data Headers

The validator checks for the presence of the following data headers. While it can interpret minor variations, using these exact names promotes an efficient review:
1. **NAME**: The chemical name (common or IUPAC).
2. **CAS**: The CAS Registry Number.
3. **ROLE**: The function of the substance (e.g., "drug substance", "process impurity").
4. **ID**: Any unique company code or identifier used in the submission.
5. **UNII**: The FDA Unique Ingredient Identifier.
6. **APPLICATION NUMBER**: The submission application number with the correct prefix (e.g., "ANDA012345", "MF012345").
7. **NOTES**: Any additional qualifying information.

---

## 3. System Requirements

- **Web Browser**: A modern web browser is required. The latest versions of Google Chrome, Mozilla Firefox, or Microsoft Edge are recommended.
- **Files**: Only one file is required: `SD_File_Validator_2_0.html`. The chemical structure rendering library is embedded directly within this file.

The tool does not require an internet connection, administrative privileges, or any additional software installation.

---

## 4. Setup Instructions

Version 2.1 of the validator is fully self-contained in a single file, which simplifies setup considerably.

1. **Obtain the File**: Download `SD_File_Validator_2_1.html`.
2. **Save to Your Computer**: Place the file anywhere on your computer that is convenient to access.

The validator is now ready to use. No additional files or configuration are needed.

---

## 5. How to Use the SD File Validator

### Step 1: Open the Validator

- Navigate to the location where you saved `SD_File_Validator_2_1.html`.
- Double-click the file. It will open in your default web browser.

### Step 2: Select Your SD File

- Click the **"Choose File"** button in the upload section.
- A file browser window will appear. Locate and select the `.sdf` or `.txt` file you wish to validate.

### Step 3: Review the Results

The tool will automatically process the file and display two main sections:

**A. Validation Report**
This section at the top provides immediate feedback on your file. It will display a "SUCCESS" message if no issues are found, or a list of color-coded "ERROR" and "WARNING" messages if issues are detected.

**B. SD File Contents**
This section displays a table containing all the data from your file. Each row represents one chemical record, showing the rendered structure next to its associated data. This allows you to quickly verify that the file was parsed correctly and to visually inspect your data.

### Step 4: Download the Report

- Click the **"Download Report"** button in the top menu bar.
- A text file named `[YourFileName]_ValidationReport.txt` will be saved to your browser's default download folder. This report contains a summary of all findings and is useful for sharing or record-keeping.

### Step 5: Validate Another File

- To check a different file, click the **"Validate Another File"** button. This will reset the tool to the initial upload screen.

---

## 6. Understanding Validation Results

### Message Types

#### ERROR (Red)
These are critical issues that violate fundamental formatting rules. **Errors must be fixed before submission.** The file is likely corrupted or will cause significant processing delays.

#### WARNING (Yellow)
These are non-critical issues or deviations from best practices. While a file with warnings may be technically processable, **it is strongly recommended that you review and address all warnings** to ensure data quality and prevent potential Information Requests from the FDA.

### Grouped Messages

To keep the report clean and readable, the validator groups identical messages. If the same issue occurs in multiple records (e.g., an empty "CAS" field), it will be reported as a single message listing all affected record numbers.
- *Example: `Record(s) 2, 5, 8: Has an empty cell for the header 'CAS'.`*

---

## 7. Common Errors and Warnings Explained

### ERROR Messages

- **"Invalid file extension. The file extension should be .sdf or .txt."**
    - **Cause**: The selected file does not have a `.sdf` or `.txt` extension.
    - **Solution**: Ensure your file is saved with the correct extension.

- **"V3000 format detected. This validator is only for V2000 SD Files..."**
    - **Cause**: The file contains MOL blocks in the V3000 format.
    - **Solution**: Re-export or convert your structures to the V2000 format.

- **"Record [X] is completely missing its MOL file block and data..."**
    - **Cause**: A record delimiter (`$$$$`) was found, but it was followed by another delimiter with no content in between.
    - **Solution**: Remove the extra blank records from your file.

- **"Record [X] has a malformed MOL block header..."**
    - **Cause**: The number of lines before the `V2000` line in the MOL block is not equal to three. A valid MOL block must have exactly three header lines (for Name, Program, and Comments), even if they are blank.
    - **Solution**: Open the file in a text editor and ensure there are exactly three lines before the counts line for the specified record.

### WARNING Messages

- **"MOL File block is empty but data was included. Please verify this is intentional for complex substances before submitting."**
    - **Cause**: The validator found data fields for a record but could not find a corresponding MOL block.
    - **Solution**: This is a prompt for verification. If the substance (e.g., a complex peptide) cannot be represented by a structure, this is acceptable. If it was an accident, add the correct MOL block to the record.

- **"Atom Notations were detected. Structure may not render properly. Please see the SD File Quick Guides on page 8 and correct the structure."**
    - **Cause**: The MOL block for the specified record contains special notation tags that are generally discouraged. The validator specifically checks for the following tags: `M  STY`, `M  SLB`, `M  SAL`, `M  SBL`, `M  SMT`, `M  SBV`, `M  RGP`, `M  SAP`, `M  SBT`, and atom-level query tags `A` and `Q`. Note that these tags are checked only in the body of the MOL block (after the three header lines) to avoid false positives from software name strings in the header.
    - **Solution**: Review page 8 of the FDA's "Quick Guide to Creating a Structure-Data File" for advice on representing special chemical features such as salts, stereochemistry, and isotopes. Remove or properly represent these features.

- **"A '[HEADER_NAME]' column was not found in the file."**
    - **Cause**: A standard header (like NAME, ROLE, or ID) is missing from all records in the file.
    - **Solution**: Add the missing data column to your SD file.

- **"The Drug Substance was not explicitly identified in the 'ROLE' column..."**
    - **Cause**: No record in the file has the term "drug substance" in its ROLE field.
    - **Solution**: Ensure at least one substance is correctly identified with the "drug substance" role.

- **"Has an empty cell for the header '[HEADER_NAME]'."**
    - **Cause**: A data field for a specific record is blank.
    - **Solution**: Populate the missing data for the specified record(s).

---

## 8. Troubleshooting

- **Problem: Structures do not render ("Render Error" message appears).**
    - **Cause**: This is almost always due to an invalid MOL block format.
    - **Solution**: Check the validation report for a "malformed MOL block header" error. Open your file in a text editor and verify that the atom and bond counts are correct and that there are exactly three lines before the `V2000` line.

- **Problem: The validator opens but structures do not render, and a "SUCCESS" message appears.**
    - **Cause**: This may indicate a browser compatibility issue or that JavaScript is disabled in your browser.
    - **Solution**: Ensure you are using a modern, supported browser (Google Chrome, Mozilla Firefox, or Microsoft Edge). Verify that JavaScript is enabled in your browser settings.

- **Problem: The "Validate Another File" button is cut off or wraps incorrectly.**
    - **Cause**: Your browser window is very narrow.
    - **Solution**: Widen your browser window. On very small screens, the buttons are designed to wrap below the main title to remain clickable.

- **Problem: The validator does not open.**
    - **Cause**: The file may not be associated with a web browser, or the browser may be blocking local file access.
    - **Solution**: Right-click `SD_File_Validator_2_1.html` and choose "Open with" to select your preferred browser (Chrome, Firefox, or Edge).

---

## 9. Support and Resources

### FDA Support Contacts

- **For formatting questions**: [FDA-SRS@fda.hhs.gov](mailto:FDA-SRS@fda.hhs.gov)
- **For DMF submission issues**: [DMFOGD@fda.hhs.gov](mailto:DMFOGD@fda.hhs.gov)

### Online Resources

- **FDA UNII Search**: [https://precision.fda.gov/uniisearch](https://precision.fda.gov/uniisearch)
- **NCATS GSRS Database**: [https://gsrs.ncats.nih.gov/ginas/app/ui/home](https://gsrs.ncats.nih.gov/ginas/app/ui/home)
- **Quick Guide for DMF Submissions**: [https://www.fda.gov/drugs/drug-master-files-dmfs/drug-master-file-dmf-submission-resources](https://www.fda.gov/drugs/drug-master-files-dmfs/drug-master-file-dmf-submission-resources)
- **Quick Guide for Other Types of Submissions (NDA, ANDA, BLA, IND)**: [https://www.fda.gov/media/161877/download?attachment](https://www.fda.gov/media/161877/download?attachment)

---

## 10. Frequently Asked Questions (FAQ)

- **Q: Does this tool send my data to the FDA?**
    - A: No. All processing happens locally in your web browser. Your data never leaves your computer.

- **Q: Do I need to download any other files besides `SD_File_Validator_2_1.html`?**
    - A: No. Version 2.1 is fully self-contained. The chemical structure rendering library is embedded directly within the HTML file, so only the single `.html` file is needed.

- **Q: My file has three blank lines before the `V2000` line. Is this okay?**
    - A: Yes. This is a valid header for a molecule with no name, program info, or comments. The validator will correctly parse this without generating a warning.

- **Q: Why did I get a warning for an empty MOL block?**
    - A: This warning appears when a record contains data (like a Name or CAS) but no structure. This is a check to ensure you did not accidentally delete the MOL block. If it is intentional (for a complex substance), you can proceed.

---

## 11. Appendix: Key SD File Requirements

- **Structure Format**: Must be V2000.
- **MOL Header**: Must contain exactly three lines before the counts line (the line with "V2000"). These can be blank.
- **Record Delimiter**: Records must be separated by `$$$$`.
- **Data Headers**: Must be enclosed in angle brackets (e.g., `> <NAME>`).
- **Excluded Content**: Do not include reagents or solvents. Avoid special atom notations or S-groups where possible; refer to SD File Quick Guide for proper representation of complex features.

---