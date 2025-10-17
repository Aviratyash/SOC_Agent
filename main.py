import json

# Import all our agent's modules
from A import validate_alert_context
from B import extract_iocs_with_llm
from C import check_ioc_reputation
from D import enrich_with_asset_details
from E import get_llm_decision_and_actions
from F import execute_actions

def start_analysis(alert_data):
    """
    Orchestrates the entire end-to-end analysis and response workflow.
    """
    # --- Step 1-4: Data Collection and Enrichment ---
    
    # 1. Validate context
    timestamp = alert_data.get('timestamp')
    validation_result = validate_alert_context(timestamp) if timestamp else "Timestamp not found."

    # 2. Extract IOCs
    extracted_iocs = extract_iocs_with_llm(alert_data)

    # 3. Check IOC Reputation
    reputation_results = {}
    if extracted_iocs:
        for ip in extracted_iocs.get("ip_addresses", []):
            reputation_results[ip] = check_ioc_reputation(ip, 'ip_address')
        for domain in extracted_iocs.get("domains", []):
            reputation_results[domain] = check_ioc_reputation(domain, 'domain')

    # 4. Enrich with Asset Context
    asset_details = enrich_with_asset_details(alert_data)

    # --- Assemble the complete investigation packet for the LLM ---
    investigation_summary = {
        "original_alert": alert_data,
        "alert_validation": validation_result,
        "extracted_iocs": extracted_iocs,
        "ioc_reputation": reputation_results,
        "asset_context": asset_details
    }

    # --- Step 5: Decision Making ---
    # The "brain" makes a decision based on the full context.
    llm_verdict = get_llm_decision_and_actions(investigation_summary)

    # --- Final Report Generation ---
    # Combine the investigation and the verdict into one final report.
    final_report = {
        "investigation_summary": investigation_summary,
        "final_verdict": llm_verdict
    }
    
    # Print the complete JSON report of the entire investigation.
    print("--- [ Final Investigation & Decision Report ] ---")
    print(json.dumps(final_report, indent=4))
    print("-------------------------------------------------")

    # --- Step 6: Action ---
    # The "hands" execute the actions decided by the "brain".
    actions_to_take = llm_verdict.get("automated_actions", [])
    execute_actions(actions_to_take)