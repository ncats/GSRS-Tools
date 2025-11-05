import zipfile
import os.path
import pathlib
from pathlib import Path
import shutil
import subprocess
import argparse

# also requires that you have the 'wget' utility in your os (e.g. via Git Bash) 

def execute_command(command):
  try:
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode("utf-8")
    error = error.decode("utf-8")
    return output, error
  except Exception as e:
    return None, str(e)

"""
This script extracts DailyMed XML files.

There are different categories of products, and each category 1 or more associated zip files.

https://dailymed.nlm.nih.gov/dailymed/spl-resources-all-drug-labels.cfm

Run for example like this 

cd path/to/workspace
python3 path/to/gsrs-tools/gsrs_products/prepare_dailymed_file_for_script.py <group> 

where group may equal 'all_dailymed_human_rx' 

See the dispatch section below.

"""

# output, error = execute_command("wget https://dailymed-data.nlm.nih.gov/public-release-files/dm_spl_release_human_rx_part2.zip")

def rmtree(folder):
    try:
        print(f"Removing '{folder}'.")
        shutil.rmtree(folder)
        print(f"Directory '{folder}' removed")
    except FileNotFoundError:
        print(f"Removing '{folder}' does not exist, so no action was taken.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def extractXmlsFromFile(dailymedZipFilename):
    print ("Extracting file: " + dailymedZipFilename)
    if (os.path.isfile(dailymedZipFilename)):
        output_dir1='xml-files1'  # where main zip file is extracted
        output_dir2='xml-files2'  # working directory should be empty after run.
        output_dir3='xml-files3'  # where final xml files used by parsing script are written. This data is later moved to "processed."
        rmtree(output_dir1)
        rmtree(output_dir2)
        rmtree(output_dir3)
        os.mkdir(output_dir1)
        os.mkdir(output_dir2)
        os.mkdir(output_dir3)
        with zipfile.ZipFile(dailymedZipFilename, 'r') as zip_ref1:
            zip_ref1.extractall(output_dir1)
            zip_ref1.close()

        for dir1 in os.listdir(output_dir1):
          _path1 =  output_dir1 +"/"+ dir1;
          if(os.path.isdir(_path1)):
            for dir2 in os.listdir(_path1):
              _path2 =  _path1 + "/" + dir2
              zip_ref2 = zipfile.ZipFile(_path2, 'r')
              infileStem = Path(dir2).stem
              newDir =os.path.join(output_dir2, infileStem)
              zip_ref2.extractall(newDir)
              for dir3 in os.listdir(newDir):
                  if(dir3.endswith(".xml")):
                    Path(newDir + "/" + dir3).rename(output_dir3 + "/" +dir3)
              shutil.rmtree(newDir)
              zip_ref2.close()
    else:
        print ("ERROR: The dailyMedZipFilename does not exist or is not a file: " + dailyMedZipFilename)

def download(url):
    output, error = execute_command("wget " + url)
    print ("dumping error")
    print (error)
    print ("dumping output")
    print (output)

def download_all_dailymed_human_rx():
    for i in range(3, 6):
        remote_file="dm_spl_release_human_rx_part" + str(i) + ".zip"
        download("https://dailymed-data.nlm.nih.gov/public-release-files/" + remote_file)

def process_all_dailymed_human_rx():
    for i in range(3, 6):
        remote_file="dm_spl_release_human_rx_part" + str(i) + ".zip"
        stem = Path(remote_file).stem
        extractXmlsFromFile(remote_file)
        output_base_path_string = 'processed/all_dailymed_human_rx'
        output_base_path = Path(output_base_path_string)
        output_base_path.mkdir(parents=True, exist_ok=True)
        shutil.move('xml-files3',  output_base_path / stem)

def download_all_dailymed_human_otc():
    for i in range(1, 11):
        remote_file="dm_spl_release_human_otc_part" + str(i) + ".zip"
        download("https://dailymed-data.nlm.nih.gov/public-release-files/" + remote_file)

def process_all_dailymed_human_otc():
    for i in range(1, 11):
        remote_file="dm_spl_release_human_otc_part" + str(i) + ".zip"
        stem = Path(remote_file).stem
        extractXmlsFromFile(remote_file)
        shutil.move('xml-files3', 'processed/' + stem)

def download_all_dailymed_homeopathic():
    remote_file="dm_spl_release_homeopathic.zip"
    download("https://dailymed-data.nlm.nih.gov/public-release-files/" + remote_file)

def process_all_dailymed_homeopathic():
    remote_file="dm_spl_release_homeopathic.zip"
    stem = Path(remote_file).stem
    extractXmlsFromFile(remote_file)
    shutil.move('xml-files3', 'processed/' + stem)

def download_all_dailymed_animal():
    remote_file="dm_spl_release_animal.zip"
    download("https://dailymed-data.nlm.nih.gov/public-release-files/" + remote_file)

def process_all_dailymed_animal():
    remote_file="dm_spl_release_animal.zip"
    stem = Path(remote_file).stem
    extractXmlsFromFile(remote_file)
    shutil.move('xml-files3', 'processed/' + stem)

def download_all_dailymed_remainder():
    remote_file="dm_spl_release_remainder.zip"
    download("https://dailymed-data.nlm.nih.gov/public-release-files/" + remote_file)

def process_all_dailymed_remainder():
    remote_file="dm_spl_release_remainder.zip"
    stem = Path(remote_file).stem
    extractXmlsFromFile(remote_file)
    shutil.move('xml-files3', 'processed/' + stem)


def all_dailymed_human_rx():
    download_all_dailymed_human_rx()
    process_all_dailymed_human_rx()

def all_dailymed_human_otc():
    download_all_dailymed_human_otc()
    process_all_dailymed_human_otc()

def all_dailymed_homeopathic():
    download_all_dailymed_homeopathic()
    process_all_dailymed_homeopathic()

def all_dailymed_animal():
    download_all_dailymed_animal()
    process_all_dailymed_animal()

def all_dailymed_remainder():
    download_all_dailymed_remainder()
    process_all_dailymed_remainder()

def testing123():
    print("Testing if dispatch method works ...")

def dispatch():
  parser = argparse.ArgumentParser("prepare_dailymed_file_for_script")
  parser.add_argument("action", help="Action to take.", type=str)
  arguments = parser.parse_args()
  action=arguments.action
  actions = {
    'all_dailymed_human_rx': True,
    'all_dailymed_human_otc': True,
    'all_dailymed_homeopathic': True,
    'all_dailymed_animal': True,
    'all_dailymed_remainder': True,
    'testing123': True,
  }
  if actions.get(action) and actions.get(action) is not None:
    # getattr(__main__, action)()
    globals()[action]()
  else:
    out = ''
    actionKeys = list(actions.keys())
    actionKeys.sort()
    for x in actionKeys:
       value = str(actions[x])
       out = out + f'{x}: {value}'+"\n"
    print(f'There is no available action called "{action}. The following are defined and runnable if True:' + "\n" + out)

dispatch()
