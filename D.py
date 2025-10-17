import csv
import os

ASSET_FILE_PATH = 'assets.csv'

def _load_asset_data():
    """
    Private function to load the asset inventory from the CSV file.
    It reads the file once and returns a list of dictionaries.
    """
    if not os.path.exists(ASSET_FILE_PATH):
        # Return an empty list and a False flag if the file is missing
        return [], False

    with open(ASSET_FILE_PATH, mode='r', encoding='utf-8') as infile:
        # Use DictReader to easily access columns by name
        reader = csv.DictReader(infile)
        return list(reader), True

def enrich_with_asset_details(alert_data):
    """
    Finds and returns details for an asset mentioned in an alert.
    It looks up the asset by matching the hostname or IP address.
    """
    assets, success = _load_asset_data()
    if not success:
        return {"error": "Asset database (assets.csv) not found."}

    # Get the primary hostname and IP from the alert's agent field
    alert_agent = alert_data.get('agent', {})
    alert_hostname = alert_agent.get('name')
    alert_ip = alert_agent.get('ip')

    # Search for a matching asset in our loaded data
    for asset in assets:
        if asset.get('hostname') == alert_hostname or asset.get('ip_address') == alert_ip:
            # Return the full details of the matched asset
            return asset
            
    # If no match is found after checking all assets
    return {"status": "Asset not found in database", "hostname": alert_hostname, "ip": alert_ip}