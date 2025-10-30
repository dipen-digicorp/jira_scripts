import os
import json
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import pytz

load_dotenv()

EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
DOMAIN = os.getenv("JIRA_DOMAIN")

BASE_URL = f"https://{DOMAIN}/rest/api/3"
auth = HTTPBasicAuth(EMAIL, API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# === CONFIGURABLE SECTION ===
ssc12_issue_id = 14733       # SSC-12
leave_issue_id = 11551       # Leave issue

regular_time_spent = "30m"
leave_full_day = "8h"
leave_half_day = "4h"
client_call_time_spent = "1h"

comment_text = "Product Standup"
client_call_comment = "Client Call"

# Dates for October 2025
start_date = datetime(2025, 10, 1)
end_date = datetime(2025, 10, 31)

# Specify leave and client call dates
public_holidays = [2,20, 21, 22]                    # public holidays
full_day_leave_dates = [ 27] # full-day leave
half_day_leave_dates = []                 # half-day leave
client_call_dates = [1, 8, 15, 30]        # client call days

local_tz = pytz.timezone("Asia/Kolkata")
current_date = start_date


def add_worklog(issue_id: int, time_spent: str, comment: str, started_str: str):
    """Helper to send one worklog"""
    payload = {
        "timeSpent": time_spent,
        "started": started_str,
        "comment": {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": comment}]}
            ]
        },
    }

    url = f"{BASE_URL}/issue/{issue_id}/worklog"
    response = requests.post(url, headers=headers, auth=auth, data=json.dumps(payload))

    if response.status_code in [200, 201]:
        print(f"✅ {comment} → {issue_id} ({time_spent})")
    else:
        print(f"❌ {comment} → {issue_id} failed: {response.status_code} {response.text}")


while current_date <= end_date:
    current_date_local = local_tz.localize(datetime(current_date.year, current_date.month, current_date.day, 9, 0))
    weekday = current_date_local.weekday()

    if weekday >= 5:
        current_date += timedelta(days=1)
        continue

    day = current_date.day
    current_date_utc = current_date_local.astimezone(pytz.utc)
    started_str = current_date_utc.strftime("%Y-%m-%dT%H:%M:%S.000%z")

    print("=======================================")
    print(f"Date: {current_date.strftime('%Y-%m-%d')} ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][weekday]})")

    if day in public_holidays:
        print("Public Holiday")

    elif day in full_day_leave_dates:
        print("Full-day leave")
        add_worklog(leave_issue_id, leave_full_day, "Full Day Leave", started_str)

    elif day in half_day_leave_dates:
        print("→Half-day leave")
        add_worklog(leave_issue_id, leave_half_day, "Half Day Leave", started_str)
        add_worklog(ssc12_issue_id, regular_time_spent, comment_text, started_str)

        if day in client_call_dates:
            add_worklog(ssc12_issue_id, client_call_time_spent, client_call_comment, started_str)

    else:
        print("Regular working day")
        add_worklog(ssc12_issue_id, regular_time_spent, comment_text, started_str)

        if day in client_call_dates:
            add_worklog(ssc12_issue_id, client_call_time_spent, client_call_comment, started_str)

    print("=======================================\n")
    current_date += timedelta(days=1)
