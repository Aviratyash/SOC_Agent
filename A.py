from datetime import datetime

# --- Constants for Validation ---
BUSINESS_HOURS_START = 9  # 9 AM
BUSINESS_HOURS_END = 17 # 5 PM (5 PM is not included, so it's 9:00 to 16:59)
BUSINESS_DAYS = [0, 1, 2, 3, 4] # Monday=0, Tuesday=1, ..., Friday=4

def validate_alert_context(alert_timestamp_str):

    try:
        alert_datetime = datetime.fromisoformat(alert_timestamp_str)
    except (ValueError, TypeError):
        return "Validation Result: Could not parse timestamp from alert."

    alert_hour = alert_datetime.hour
    alert_weekday = alert_datetime.weekday()

    if alert_weekday in BUSINESS_DAYS:
        day_context = "Business Day"
        if BUSINESS_HOURS_START <= alert_hour < BUSINESS_HOURS_END:
            time_context = "During Business Hours"
        else:
            time_context = "Outside Business Hours"
    else:
        day_context = "Weekend"
        time_context = "Outside Business Hours"
    
    return f"Validation Result: Alert occurred on a {day_context}, {time_context}."