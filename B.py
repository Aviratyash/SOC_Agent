import json
import os
import requests
from dotenv import load_dotenv  # Import the function to load the .env file

# Load environment variables from the .env file
load_dotenv()

def _build_llm_prompt(alert_json_string):
    """
    Creates a simple prompt for the LLM to extract IOCs.
    """
    prompt = f"""
You are a SOC analyst. Extract IOCs from the following alert.
Respond ONLY with a JSON object with these keys: "ip_addresses", "urls", "domains", "file_hashes", "user_accounts".
If a key has no value, use an empty list [].

Alert:
{alert_json_string}

JSON Response:
"""
    return prompt

def call_mistral_api_simple(prompt):
    """
    Makes a direct, simple API call to the Mistral endpoint.
    """
    # Now we get the API key that was loaded from the .env file
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Error: MISTRAL_API_KEY not found in the .env file.")
        return None

    api_url = "https://api.mistral.ai/v1/chat/completions"
    
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        print("--- [ Calling Mistral API Directly... ] ---")
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        print("--- [ API Call Successful ] ---")

        response_data = response.json()
        return response_data['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        print(f"An error occurred making the API request: {e}")
        return None

def extract_iocs_with_llm(alert_data):
    """
    Uses a direct Mistral API call to extract IOCs from an alert.
    """
    alert_json_string = json.dumps(alert_data)
    prompt = _build_llm_prompt(alert_json_string)
    llm_response_string = call_mistral_api_simple(prompt)

    if llm_response_string:
        try:
            return json.loads(llm_response_string)
        except json.JSONDecodeError:
            print("Error: Could not decode the JSON response from the API.")
    
    return {
        "ip_addresses": [], "urls": [], "domains": [], 
        "file_hashes": [], "user_accounts": []
    }