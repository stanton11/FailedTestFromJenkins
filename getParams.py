import os
import requests
import tarfile
import xml.etree.ElementTree as ET
import logging
from tqdm import tqdm

# URLs of the zip files
ZIP_FILE_URLS = [
    "http://qa.sc.couchbase.com/view/Cloud/job/k8s-cbop-aks-pipeline/lastSuccessfulBuild/artifact/validation.tar.gz",
    "http://qa.sc.couchbase.com/view/Cloud/job/k8s-cbop-aks-pipeline/lastSuccessfulBuild/artifact/sanity.tar.gz",
    # "http://qa.sc.couchbase.com/view/Cloud/job/k8s-cbop-aks-pipeline/lastSuccessfulBuild/artifact/p0.tar.gz",
    # "http://qa.sc.couchbase.com/view/Cloud/job/k8s-cbop-aks-pipeline/lastSuccessfulBuild/artifact/p1.tar.gz",
    # Add more URLs as needed
]

# Directory to store downloaded and extracted files
DOWNLOAD_DIR = "downloaded_files"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_file(url, target_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        with open(target_path, "wb") as file, tqdm(
            desc=os.path.basename(target_path),
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
                bar.update(len(chunk))
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file from URL '{url}': {e}")
        return False


def extract_tar_archive(archive_path, extract_dir):
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(extract_dir)
        return True
    except tarfile.TarError as e:
        logger.error(f"Error extracting archive '{archive_path}': {e}")
        return False


def parse_xml(xml_file_path):
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Extract 'testcase name' and check for 'failure message'
        for testcase in root.findall(".//testcase"):
            testcase_name = testcase.get("name")
            failure = testcase.find("failure")

            if testcase_name and failure is not None:
                # If 'failure' element exists, add 'testcase name' to the set
                unique_testcases_with_failures.add(testcase_name)

        logger.info(
            f"Testcase names with failures extracted from XML file '{xml_file_path}'"
        )
    except ET.ParseError as e:
        logger.error(f"Error parsing XML file '{xml_file_path}': {e}")


if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Set to store unique 'testcase names' with a 'failure message'
    unique_testcases_with_failures = set()

    for zip_file_url in ZIP_FILE_URLS:
        zip_file_path = os.path.join(DOWNLOAD_DIR, os.path.basename(zip_file_url))

        if download_file(zip_file_url, zip_file_path) and extract_tar_archive(
            zip_file_path, DOWNLOAD_DIR
        ):
            # Iterate through XML files in the extracted directory
            for xml_file_name in os.listdir(DOWNLOAD_DIR):
                if xml_file_name.endswith(".xml"):
                    xml_file_path = os.path.join(DOWNLOAD_DIR, xml_file_name)
                    parse_xml(xml_file_path)

    # Convert the set to a list for final output
    testcases_with_failures_list = list(unique_testcases_with_failures)

    # Print the final list containing unique 'testcase names' with 'failure messages'
    logger.info("Unique Testcase names with failures:")
    logger.info(testcases_with_failures_list)
