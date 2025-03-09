import json
import requests



# Load and parse the JSON file
def load_config(file_path):
    """file_path (str): storage path of json file"""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error loading JSON file: {str(e)}")
        return None
        

# Save data to file_path.json
def save_config(file_path, data, indent=4, ensure_ascii=False):
    """    
    params:
        file_path (str): storage path of json file
        data (dict/list): datas need to save
        indent (int): number of indented spaces, default is 4
        ensure_ascii (bool): if or not ensure ASCII encoding, default is False to support non-ASCII characters like Chinese.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=indent, ensure_ascii=ensure_ascii, sort_keys=True)
        return True
    except Exception as e:
        print(f"Error saving JSON file: {str(e)}")
        return False


# Organize the data into a format suitable for HTTP transmission
def organize_data(config_data):
    switches = config_data.get("Switches", [])
    hosts = config_data.get("Hosts", [])
    links = config_data.get("Links", [])

    organized_data = {
        "switches": switches,
        "hosts": hosts,
        "links": links
    }
    return organized_data


# Send the data via HTTP POST request
def send_data_to(data, url):
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        print(f"Data sent successfully. Status code: {response.status_code}")
        print("Response from server:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error sending data:", e)


# Main function to run the process
def main():
    # Path to the config.json file
    config_file = "config.json"
    # Replace with your frontend API endpoint
    api_url = "http://127.0.0.1:3000/network-data"

    # Load and parse the configuration data
    config_data = load_config(config_file)

    # Organize the data
    formatted_data = organize_data(config_data)

    print(formatted_data)
    # Send the data to the frontend
    send_data_to(formatted_data, api_url)


if __name__ == "__main__":
    main()
