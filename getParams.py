import sys
import requests
from bs4 import BeautifulSoup


def extract_params_from_webpage(url):
    # Fetch the HTML content of the webpage
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all settings and extract key/value pairs
        settings = soup.find_all("td", {"class": "setting-name"})

        # Initialize a list to store key/value pairs
        key_value_pairs = []

        for setting in settings:
            key = setting.text.strip()

            # Find the next "value" after "setting-main"
            value_element = setting.find_next("td", {"class": "setting-main"}).find(
                "input", {"name": "value"}
            )

            # Check if the value is a checkbox
            if value_element and value_element.get("type") == "checkbox":
                value = "checked" if value_element.get("checked") else "unchecked"
            else:
                value = value_element.get("value", "")

            key_value_pairs.append((key, value))

        # Display the key/value pairs
        for key, value in key_value_pairs:
            print(f"{key}: {value}")
    else:
        print(f"Failed to fetch the webpage. Status Code: {response.status_code}")


if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python script.py <job_input>")
        sys.exit(1)

    # Extract the job input from the command-line arguments
    job_input = sys.argv[1]

    # Construct the URL
    url_to_extract = (
        f"http://qa.sc.couchbase.com/view/Cloud/job/{job_input}/parameters/"
    )

    # Call the function to extract and display parameters
    extract_params_from_webpage(url_to_extract)
