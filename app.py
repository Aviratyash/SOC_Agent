from flask import Flask, render_template, jsonify, session
import json
import random
import os

# Import all our agent's modules
from A import validate_alert_context
from B import extract_iocs_with_llm
from C import check_ioc_reputation
from D import enrich_with_asset_details
from E import get_llm_decision_and_actions
from F import execute_actions

app = Flask(__name__)
app.secret_key = os.urandom(24)

def load_alerts():
    """Loads alerts from the JSON file."""
    try:
        with open('alerts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"error": "alerts.json not found"}]

ALERTS = load_alerts()

@app.route('/')
def index():
    """Renders the main user interface."""
    return render_template('index.html')

@app.route('/start_analysis', methods=['POST'])
def start_analysis_route():
    """Selects a random alert and initializes the investigation."""
    selected_alert = random.choice(ALERTS)
    session['alert_data'] = selected_alert
    session['investigation_summary'] = {"original_alert": selected_alert}
    return jsonify(selected_alert)

@app.route('/run_step/<step_name>', methods=['POST'])
def run_step_route(step_name):
    """Runs a single step of the analysis pipeline."""
    alert_data = session.get('alert_data')
    summary = session.get('investigation_summary', {})
    
    if not alert_data:
        return jsonify({"error": "Analysis not started."}), 400
    
    result = {}
    
    if step_name == 'validate':
        timestamp = alert_data.get('timestamp')
        result = validate_alert_context(timestamp) if timestamp else {"error": "Timestamp not found"}
        summary['alert_validation'] = result
    
    elif step_name == 'extract_iocs':
        result = extract_iocs_with_llm(alert_data)
        summary['extracted_iocs'] = result
    
    elif step_name == 'check_reputation':
        iocs = summary.get('extracted_iocs', {})
        reputation_results = {}
        for ip in iocs.get("ip_addresses", []):
            reputation_results[ip] = check_ioc_reputation(ip, 'ip_address')
        result = reputation_results
        summary['ioc_reputation'] = result
    
    elif step_name == 'enrich_context':
        result = enrich_with_asset_details(alert_data)
        summary['asset_context'] = result
    
    elif step_name == 'decide':
        result = get_llm_decision_and_actions(summary)
        summary['final_verdict'] = result
    
    elif step_name == 'execute':
        actions = summary.get('final_verdict', {}).get('automated_actions', [])
        result = actions if actions else []
    
    session['investigation_summary'] = summary
    return jsonify({step_name: result})

if __name__ == '__main__':
    app.run(debug=True)
