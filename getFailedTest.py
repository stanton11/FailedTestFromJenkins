import os
import requests
import tarfile
import xml.etree.ElementTree as ET
import glob
from tqdm import tqdm
import subprocess
import argparse
import shutil


# Function to convert string to boolean
def str_to_bool(s):
    return s.lower() == "true"


# Set download directory
download_dir = "downloaded_files"


def install_prerequisites():
    # Install required packages
    try:
        subprocess.run(["pip", "install", "requests", "tqdm", "html5lib"])
    except Exception as e:
        print(f"Error installing prerequisites: {e}")
        exit(1)

    # Import the installed packages and argparse
    import requests
    from tqdm import tqdm


def str_to_bool(s):
    return s.lower() == "true"


# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process URLs with a given pipeline name"
    )
    parser.add_argument("pipeline_name", help="Name of the pipeline")
    parser.add_argument(
        "url1", type=str_to_bool, help="Enable or disable the first URL"
    )
    parser.add_argument(
        "url2", type=str_to_bool, help="Enable or disable the second URL"
    )
    parser.add_argument(
        "url3", type=str_to_bool, help="Enable or disable the third URL"
    )
    parser.add_argument(
        "url4", type=str_to_bool, help="Enable or disable the fourth URL"
    )
    return parser.parse_args()


# Generate URL list based on command-line arguments
def generate_zip_file_urls(args):
    url_template = (
        "http://qa.sc.couchbase.com/view/Cloud/job/{pipeline}/artifact/{file}"
    )
    urls = [
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
    return [url for url in urls if url is not None]


# Download and extract files from the zip archive
def download_and_extract(zip_file_url):
    try:
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

        extracted_dir = os.path.join(
            download_dir, os.path.splitext(os.path.basename(zip_file_path))[0]
        )
        os.makedirs(extracted_dir, exist_ok=True)

        shutil.unpack_archive(zip_file_path, extracted_dir)

        print(f"Extracted files to: {extracted_dir}")
        return os.path.abspath(extracted_dir)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading or processing URL '{zip_file_url}': {e}")
        return None


# Process XML files and extract test cases with failures
def process_xml_files(extracted_dir):
    xml_files = glob.glob(os.path.join(extracted_dir, "**", "*.xml"), recursive=True)
    unique_testcases_with_failures = set()

    for xml_file_path in xml_files:
        print(f"Processing XML file: {xml_file_path}")

        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            for testcase in root.findall(".//testcase[failure]"):
                testcase_name = testcase.get("name")
                failure = testcase.find("failure")

                if testcase_name and failure is not None:
                    unique_testcases_with_failures.add(testcase_name)

            print(
                f"Testcase names with failures extracted from XML file '{xml_file_path}'"
            )

        except ET.ParseError as e:
            print(f"Error parsing XML file '{xml_file_path}': {e}")

    return unique_testcases_with_failures


# Remove downloaded files
def remove_downloaded_files():
    try:
        for zip_file_url in zip_file_urls:
            if zip_file_url:
                zip_file_path = os.path.join(
                    download_dir, os.path.basename(zip_file_url)
                )
                extracted_dir = os.path.join(
                    download_dir, os.path.splitext(os.path.basename(zip_file_path))[0]
                )

                os.remove(zip_file_path)
                shutil.rmtree(extracted_dir)

                print(f"Removed files related to: {zip_file_url}")

    except Exception as e:
        print(f"Error removing downloaded files: {e}")


# Convert set to a string for final output
def set_to_string(unique_testcases_with_failures):
    return (
        "-test " + " -test ".join(unique_testcases_with_failures)
        if unique_testcases_with_failures
        else ""
    )


# Main function
def main():
    # Install prerequisites
    install_prerequisites()

    # Parse command-line arguments
    args = parse_arguments()

    # Generate URLs based on command-line arguments
    global zip_file_urls
    zip_file_urls = generate_zip_file_urls(args)

    # Create the download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)

    # Set to store unique 'testcase names' with a 'failure message'
    unique_testcases_with_failures = set()

    # Iterate through zip file URLs
    for zip_file_url in zip_file_urls:
        extracted_dir = download_and_extract(zip_file_url)

        if extracted_dir:
            unique_testcases_with_failures.update(process_xml_files(extracted_dir))

    # Print the final string containing unique 'testcase names' with 'failure messages'
    output_string = set_to_string(unique_testcases_with_failures)
    print("Unique Testcase names with failures:")
    print(output_string)

    # Remove downloaded files
    remove_downloaded_files()


if __name__ == "__main__":
    main()
