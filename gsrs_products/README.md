# `gsrs_products` tools

These tools help with uploading product data. Currently the focus is on DailyMed, but the tools will expand to other sources.

## Working with DailyMed data

### Get started

Clone the gsrs-tools and set some variables to mark the code and data locations. This helps us keep data out of the repository

Any time you start a new session create these or similar environment variables.

```
export workspace=path/to/workspace
export code=path/to/gsrs-tools/gsrs_products

cd $workspace
```

clean up/remove any files and folders from a previous workspace session. You can process multiple DailyMed zip files. The output for each zip file will be placed in its own individual folder. However, if you have folders in processed-xml from previous work-sessions, you should delete them.

In the steps below, we focus on one DailyMed data group: `_human_rx`.  You would repeat the process for any other groups you are interested in.

### Step 1 -- Download and extract the XML files

```
python3 $code/prepare_dailymed_file_for_script.py all_dailymed_human_rx
```

This will download zip files from DailyMed for the group, and will extract them into a folder structure that looks like this:

```
processed-xml
  all_dailymed_human_rx
    dm_spl_release_human_rx_part1
      000114da-959d-4159-bd00-22d9b7faad4d.xml
      000e0356-cc97-4c3c-a0f7-57dcf0c52e30.xml
      0013824B-6AEE-4DA4-AFFD-35BC6BF19D91.xml
      ...
    dm_spl_release_human_rx_part2
    ... 
```

### Step 2 -- Convert DailyMed XMLs to JSON and place them in a Zip file

```
mkdir -p processed-json-zip

python3 $code/xml_parser_productlevel.py processed-xml/all_dailymed_human_rx processed-json-zip/all_dailymed_human_rx-jsons.zip
```

In this case, any .xml file recursively found in the all_dailymed_human_rx folder will be converted to JSON and included in the output zip file.

## Step 3 -- Upload all the JSON files in the Zip using API calls

First, set environment variables for uploader as needed.

```
export DEBUG=FALSE
export REQUEST_METHOD=POST # or PUT
export AUTH_USERNAME=admin
export AUTH_METHOD=password # or key
export AUTH_PASSWORD=XXXXXX
export AUTH_KEY=XXXXXX
export TARGET_URL="http://localhost:8081/ginas/app/api/v1/products"

```

Next, run:

```
python3 $code/uploader.py processed-json-zip/all_dailymed_human_rx-jsons.zip
```
