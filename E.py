import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def _build_decision_prompt(investigation_data_json):
    """
    Creates a prompt for the LLM to analyze data and decide on specific actions.
    """
    prompt = f"""
You are an autonomous Level 2 SOC analyst agent. You have been provided with a complete investigation packet.

Your task is to:
1.  Write a concise summary of the event.
2.  Classify the attack pattern.
3.  Assign a final severity rating (Low, Medium, High, or Critical).
4.  Decide which automated actions to take from the list of available tools.

Your available tools are:
- "block_ip": Blocks an IP address at the firewall.
- "isolate_host": Disconnects a host from the network.
- "disable_user": Disables a user account in Active Directory.

You MUST provide your response in a single, clean JSON object with the following keys: "analyst_summary", "attack_category", "final_severity", and "automated_actions".

The "automated_actions" key MUST contain a JSON array of objects, where each object has two keys: "action" (the tool name) and "target" (the IP, hostname, or username to act upon). If no action is needed, return an empty array [].

--- INVESTIGATION DATA ---
{investigation_data_json}
--- END INVESTIGATION DATA ---

JSON Response:
"""
    return prompt

def _call_mistral_api(prompt):
    """
    Makes a direct API call to the Mistral endpoint.
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return {"error": "MISTRAL_API_KEY not found in .env file."}

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
        print("--- [ LLM is making a decision... ] ---")
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        print("--- [ Decision received ] ---")
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"API request failed: {e}"})

def get_llm_decision_and_actions(investigation_data):
    """
    Takes the complete investigation data, sends it to the LLM for a decision,
    and returns the analysis and a list of actions.
    """
    investigation_data_json = json.dumps(investigation_data, indent=2)
    prompt = _build_decision_prompt(investigation_data_json)
    llm_response_string = _call_mistral_api(prompt)

    try:
        return json.loads(llm_response_string)
    except (json.JSONDecodeError, TypeError):
        return {
            "analyst_summary": "Failed to get a valid decision from LLM.",
            "attack_category": "Unknown",
            "final_severity": "Undetermined",
            "automated_actions": []
        }