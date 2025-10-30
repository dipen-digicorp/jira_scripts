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

issue_id = 14733  # SSC-12

time_spent = "30m"
comment_text = "Product Standup"

start_date = datetime(2025, 10, 1)
end_date = datetime(2025, 10, 31)

current_date = start_date
local_tz = pytz.timezone("Asia/Kolkata")

while current_date <= end_date:
    # Create timezone-aware datetime for 9 AM IST
    current_date_local = local_tz.localize(datetime(current_date.year, current_date.month, current_date.day, 9, 0))

    # Skip Saturday (5) and Sunday (6)
    if current_date_local.weekday() < 5:
        current_date_utc = current_date_local.astimezone(pytz.utc)
        started_str = current_date_utc.strftime("%Y-%m-%dT%H:%M:%S.000%z")

        print("=======================================")
        print(f"Local Date: {current_date_local.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
        print(f"UTC Date:   {current_date_utc.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
        print(f"Sent to Jira (started): {started_str}")
        print(f"Weekday: {current_date_local.weekday()}")

        payload = {
            "timeSpent": time_spent,
            "started": started_str,
            "comment": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment_text}]
                    }
                ]
            }
        }

        url = f"{BASE_URL}/issue/{issue_id}/worklog"
        response = requests.post(url, headers=headers, auth=auth, data=json.dumps(payload))

        if response.status_code in [200, 201]:
            print(f"✅ Worklog added for {current_date_local.strftime('%Y-%m-%d')}")
        else:
            print(f"❌ Failed for {current_date_local.strftime('%Y-%m-%d')}: {response.status_code} {response.text}")
        print("=======================================\n")

    current_date += timedelta(days=1)
