import sys
import requests
from bs4 import BeautifulSoup


def extract_params_from_webpage(url):
    # Fetch the HTML content of the webpage
    response = requests.get(url)

    # Initialize a list to store key/value pairs
    key_value_pairs = {}

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all settings and extract key/value pairs
        settings = soup.find_all("td", {"class": "setting-name"})

        for setting in settings:
            key = setting.text.strip()

            # Find the next "value" after "setting-main"
            value_element = setting.find_next("td", {"class": "setting-main"}).find(
                "input", {"name": "value"}
            )

            # Check if the value is a checkbox
            if value_element and value_element.get("type") == "checkbox":
                value = "true" if value_element.get("checked") else "false"
            else:
                value = value_element.get("value", "")

            key_value_pairs[key] = value
    else:
        print(f"Failed to fetch the webpage. Status Code: {response.status_code}")

    return key_value_pairs


def format_output(params):
    output_string = [""]

    # Display the key/value pairs
    for key in params:
        if key == "lpv" or key == "enable_istio" or key == "platformcert":
            output_string.append(
                f"booleanParam(name: '{key}', value: '{params[key]}'),"
            )
        elif key == "validation" or key == "sanity" or key == "p0" or key == "p1":
            output_string.append(f"booleanParam(name: '{key}', value: 'false')")
        elif key == "custom" or key == "custom_args":
            continue
        else:
            output_string.append(f"string(name: '{key}', value: '{params[key]}'),")

    # Join the list of strings into a single string
    result_string = "".join(output_string)

    print(result_string)
    print(params["validation"])
    print(params["sanity"])
    print(params["p0"])
    print(params["p1"])
    print(params["custom"])


if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python script.py <job_name> <build_num>")
        sys.exit(1)

    # Extract the job input from the command-line arguments
    job_input = sys.argv[1]
    build_num = sys.argv[2]

    # Construct the URL
    url_to_extract = (
        f"http://172.23.109.231/view/Cloud/job/{job_input}/{build_num}/parameters/"
    )

    # Call the function to extract and display parameters
    pairs = extract_params_from_webpage(url_to_extract)

    # Call the function to format the params ready for the build job
    format_output(pairs)
