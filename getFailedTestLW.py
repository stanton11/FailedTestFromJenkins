import os
import requests
import tarfile
import xml.etree.ElementTree as ET
import glob
import subprocess
import argparse
import shutil


def str_to_bool(s):
    return s.lower() == "true"


def install_prerequisites():
    try:
        subprocess.run(["pip", "install", "requests", "html5lib"])
    except Exception as e:
        print(f"Error installing prerequisites: {e}")
        exit(1)


download_dir = "downloaded_files"


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
    parser.add_argument(
        "url5", type=str_to_bool, help="Enable or disable the fifth URL"
    )
    return parser.parse_args()


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
        url_template.format(pipeline=args.pipeline_name, file="custom.tar.gz")
        if args.url5
        else None,
    ]
    return [url for url in urls if url is not None]


def download_and_extract(zip_file_url):
    try:
        zip_file_path = os.path.join(download_dir, os.path.basename(zip_file_url))
        with requests.get(zip_file_url, stream=True) as response, open(
            zip_file_path, "wb"
        ) as file:
            file.write(response.content)

        extracted_dir = os.path.join(
            download_dir, os.path.splitext(os.path.basename(zip_file_path))[0]
        )
        os.makedirs(extracted_dir, exist_ok=True)

        shutil.unpack_archive(zip_file_path, extracted_dir)

        return os.path.abspath(extracted_dir)

    except requests.exceptions.RequestException as e:
        print(f"Error downloading or processing URL '{zip_file_url}': {e}")
        return None


def process_xml_files(extracted_dir):
    xml_files = glob.glob(os.path.join(extracted_dir, "**", "*.xml"), recursive=True)
    unique_testcases_with_failures = set()

    for xml_file_path in xml_files:
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            for testcase in root.findall(".//testcase[failure]"):
                testcase_name = testcase.get("name")
                failure = testcase.find("failure")

                if testcase_name and failure is not None:
                    unique_testcases_with_failures.add(testcase_name)

        except ET.ParseError as e:
            print(f"Error parsing XML file '{xml_file_path}': {e}")

    return unique_testcases_with_failures


def set_to_string(unique_testcases_with_failures):
    return (
        "-test " + " -test ".join(unique_testcases_with_failures)
        if unique_testcases_with_failures
        else ""
    )


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

    except Exception as e:
        print(f"Error removing downloaded files: {e}")


def main():
    install_prerequisites()
    args = parse_arguments()
    global zip_file_urls
    zip_file_urls = generate_zip_file_urls(args)
    os.makedirs(download_dir, exist_ok=True)
    unique_testcases_with_failures = set()

    for zip_file_url in zip_file_urls:
        extracted_dir = download_and_extract(zip_file_url)

        if extracted_dir:
            unique_testcases_with_failures.update(process_xml_files(extracted_dir))

    output_string = set_to_string(unique_testcases_with_failures)
    # print("Unique Testcase names with failures:")

    print(
        f"booleanParam(name: 'custom', value: true), string(name: 'custom_args', value: '{output_string}')"
    )

    # Remove downloaded files
    remove_downloaded_files()


if __name__ == "__main__":
    main()
