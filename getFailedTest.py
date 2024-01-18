import os
import requests
import tarfile
import xml.etree.ElementTree as ET
import glob
from tqdm import tqdm
import subprocess
import argparse
import shutil

# Install required packages
try:
    subprocess.run(["pip", "install", "requests", "tqdm", "html5lib"])
except Exception as e:
    print(f"Error installing prerequisites: {e}")
    exit(1)

# Import the installed packages and argparse
import requests
from tqdm import tqdm


# Function to convert string to boolean
def str_to_bool(s):
    return s.lower() == "true"


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Process URLs with a given pipeline name")
parser.add_argument("pipeline_name", help="Name of the pipeline")
parser.add_argument("url1", type=str_to_bool, help="Enable or disable the first URL")
parser.add_argument("url2", type=str_to_bool, help="Enable or disable the second URL")
parser.add_argument("url3", type=str_to_bool, help="Enable or disable the third URL")
parser.add_argument("url4", type=str_to_bool, help="Enable or disable the fourth URL")
args = parser.parse_args()

# URL template with a placeholder for the pipeline name
url_template = "http://qa.sc.couchbase.com/view/Cloud/job/{pipeline}/lastSuccessfulBuild/artifact/{file}"

# URLs of the zip files based on command-line arguments
zip_file_urls = [
    url_template.format(pipeline=args.pipeline_name, file="validation.tar.gz")
    if args.url1
    else None,
    url_template.format(pipeline=args.pipeline_name, file="sanity.tar.gz")
    if args.url2
    else None,
    url_template.format(pipeline=args.pipeline_name, file="p0.tar.gz")
    if args.url3
    else None,
    url_template.format(pipeline=args.pipeline_name, file="p1.tar.gz")
    if args.url4
    else None,
]

# Remove any None values from the list
zip_file_urls = [url for url in zip_file_urls if url is not None]

# Directory to store downloaded and extracted files
download_dir = "downloaded_files"

# Create the download directory if it doesn't exist
os.makedirs(download_dir, exist_ok=True)

# Set to store unique 'testcase names' with a 'failure message'
unique_testcases_with_failures = set()


# Function to download and extract files from the zip archive
def download_and_extract(zip_file_url):
    try:
        # Download the zip file with progress bar
        zip_file_path = os.path.join(download_dir, os.path.basename(zip_file_url))
        with requests.get(zip_file_url, stream=True) as response, open(
            zip_file_path, "wb"
        ) as file, tqdm(
            desc=os.path.basename(zip_file_path),
            total=int(response.headers.get("content-length", 0)),
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                bar.update(len(data))
                file.write(data)

        print(f"\nDownloaded the zip file to: {zip_file_path}")

        # Extract files from the zip archive
        extracted_dir = os.path.join(
            download_dir, os.path.splitext(os.path.basename(zip_file_path))[0]
        )
        os.makedirs(extracted_dir, exist_ok=True)

        with tarfile.open(zip_file_path, "r:gz") as tar:
            tar.extractall(extracted_dir)

        print(f"Extracted files to: {extracted_dir}")

        # Return the path to the extracted directory
        return extracted_dir

    except requests.exceptions.RequestException as e:
        print(f"Error downloading or processing URL '{zip_file_url}': {e}")
        return None


# Iterate through zip file URLs
for zip_file_url in zip_file_urls:
    extracted_dir = download_and_extract(zip_file_url)

    if extracted_dir:
        # Adjusted path to point to XML files directly
        xml_files = glob.glob(
            os.path.join(extracted_dir, "**", "*.xml"), recursive=True
        )

        # Iterate through XML files
        for xml_file_path in xml_files:
            print(f"Processing XML file: {xml_file_path}")

            try:
                tree = ET.parse(xml_file_path)
                root = tree.getroot()

                # Extract 'testcase name' with 'failure message'
                for testcase in root.findall(".//testcase[failure]"):
                    testcase_name = testcase.get("name")
                    failure = testcase.find("failure")

                    if testcase_name and failure is not None:
                        # If 'failure' element exists, add 'testcase name' to the set
                        unique_testcases_with_failures.add(testcase_name)

                print(
                    f"Testcase names with failures extracted from XML file '{xml_file_path}'"
                )

            except ET.ParseError as e:
                print(f"Error parsing XML file '{xml_file_path}': {e}")

# Convert the set to a list for final output
testcases_with_failures_list = list(unique_testcases_with_failures)

# Generate the final output string
output_string = (
    "-test " + " -test ".join(testcases_with_failures_list)
    if testcases_with_failures_list
    else ""
)

# Print the final output string
print(output_string)

# Section to remove downloaded files
try:
    for zip_file_url in zip_file_urls:
        if zip_file_url:
            zip_file_path = os.path.join(download_dir, os.path.basename(zip_file_url))
            extracted_dir = os.path.join(
                download_dir, os.path.splitext(os.path.basename(zip_file_path))[0]
            )

            # Remove downloaded zip file
            os.remove(zip_file_path)

            # Remove extracted directory
            shutil.rmtree(extracted_dir)

            print(f"Removed files related to: {zip_file_url}")

except Exception as e:
    print(f"Error removing downloaded files: {e}")
