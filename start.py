import json
import random
import os

# We will import the main engine function from our upcoming main.py file.
# For now, this line assumes a function named 'start_analysis' will exist there.
from main import start_analysis

def trigger_analysis_workflow():
    alerts_file_name = 'alerts.json'

    try:
        # Open the JSON file and load all the alerts into a list.
        with open(alerts_file_name, 'r') as file:
            alerts = json.load(file)

        selected_alert = random.choice(alerts)

        start_analysis(selected_alert)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# This is the standard entry point for a Python script.
# It ensures the code inside only runs when you execute 'python start.py'.
if __name__ == "__main__":
    trigger_analysis_workflow()