import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
DOMAIN = os.getenv("JIRA_DOMAIN")

BASE_URL = f"https://{DOMAIN}/rest/api/3"
auth = HTTPBasicAuth(EMAIL, API_TOKEN)
headers = {"Accept": "application/json"}

# === CONFIGURE HERE ===
issue_id = 14733  # e.g. SSC-12
start_date = datetime(2025, 10, 1)
end_date = datetime(2025, 10, 31)
# ======================

def parse_jira_time(ts: str) -> datetime:
    """Parse Jira timestamp like 2025-10-01T03:30:00.000+0000"""
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.000%z")

def get_worklogs(issue_id: int):
    url = f"{BASE_URL}/issue/{issue_id}/worklog"
    resp = requests.get(url, headers=headers, auth=auth)
    resp.raise_for_status()
    return resp.json().get("worklogs", [])

def delete_worklog(issue_id: int, worklog_id: str):
    url = f"{BASE_URL}/issue/{issue_id}/worklog/{worklog_id}"
    resp = requests.delete(url, headers=headers, auth=auth)
    return resp.status_code

def main():
    print(f"Fetching worklogs for issue {issue_id}...\n")
    worklogs = get_worklogs(issue_id)
    deleted_count = 0

    for wl in worklogs:
        started_str = wl.get("started")
        author_email = wl.get("author", {}).get("emailAddress", "")
        worklog_id = wl.get("id")
        display_name = wl.get("author", {}).get("displayName", "")

        # Skip if not my worklog
        if author_email.lower() != EMAIL.lower():
            continue

        # Parse and check date range
        try:
            started_dt = parse_jira_time(started_str)
        except Exception:
            continue

        if start_date <= started_dt.replace(tzinfo=None) <= end_date:
            print(f"🗑️  Deleting my worklog {worklog_id} dated {started_dt}")
            status = delete_worklog(issue_id, worklog_id)
            if status == 204:
                print("✅ Deleted successfully\n")
                deleted_count += 1
            else:
                print(f"❌ Failed ({status})\n")

    print(f"Total deleted: {deleted_count}")

if __name__ == "__main__":
    main()
