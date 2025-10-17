import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def check_ioc_reputation(ioc_value, ioc_type):
    """
    Checks the reputation of an IOC (IP, domain, or URL) using the VirusTotal API.
    """
    api_key = os.getenv("VT_API_KEY")
    if not api_key:
        return "Reputation Check Failed: VIRUSTOTAL_API_KEY not found in .env file."

    # Determine the correct API endpoint based on the IOC type
    if ioc_type == 'ip_address':
        endpoint = f"https://www.virustotal.com/api/v3/ip_addresses/{ioc_value}"
    elif ioc_type == 'domain':
        endpoint = f"https://www.virustotal.com/api/v3/domains/{ioc_value}"
    elif ioc_type == 'url':
        # URLs need to be handled differently by the VT API, but for now we keep it simple.
        # A full implementation would involve submitting the URL for scanning if not found.
        # This is a simplified lookup.
        endpoint = f"https://www.virustotal.com/api/v3/urls/{ioc_value}" # This lookup is for known URLs
    else:
        return f"Reputation Check Failed: Unsupported IOC type '{ioc_type}'."

    headers = {
        "x-apikey": api_key
    }

    try:
        print(f"--- [ Checking VirusTotal for {ioc_type}: {ioc_value} ] ---")
        response = requests.get(endpoint, headers=headers)
        
        # Raise an error if the request failed (e.g., 401 Unauthorized, 429 Rate Limit)
        response.raise_for_status()

        response_data = response.json()
        
        # Get the analysis statistics
        stats = response_data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
        malicious_count = stats.get('malicious', 0)
        
        if malicious_count > 0:
            return f"Result: MALICIOUS ({malicious_count} vendors flagged this IOC)."
        else:
            return "Result: Benign (0 vendors flagged this IOC)."

    except requests.exceptions.HTTPError as e:
        # Specifically handle the 'Not Found' error, which is common
        if e.response.status_code == 404:
            return "Result: Not found in VirusTotal database."
        # Handle other HTTP errors (like bad API key or rate limiting)
        return f"Reputation Check Failed: An API error occurred - {e}"
    except requests.exceptions.RequestException as e:
        # Handle network-level errors
        return f"Reputation Check Failed: A network error occurred - {e}"