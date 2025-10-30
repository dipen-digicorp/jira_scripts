import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dotenv import load_dotenv
import pytz

# === LOAD ENV ===
load_dotenv()
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
DOMAIN = os.getenv("JIRA_DOMAIN")

BASE_URL = f"https://{DOMAIN}/rest/api/3"
auth = HTTPBasicAuth(EMAIL, API_TOKEN)
headers = {"Accept": "application/json"}

# === CONFIGURE HERE ===
issue_ids = [14733, 11551] 
start_date = datetime(2025, 11, 1)
end_date = datetime(2025, 11, 6)
dry_run = False  # True = preview only, False = actually delete
# =======================

local_tz = pytz.timezone("Asia/Kolkata")


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
    total_deleted = 0

    for issue_id in issue_ids:
        print(f"\n Fetching worklogs for issue {issue_id}...")
        worklogs = get_worklogs(issue_id)
        deleted_count = 0

        for wl in worklogs:
            started_str = wl.get("started")
            author_email = wl.get("author", {}).get("emailAddress", "")
            display_name = wl.get("author", {}).get("displayName", "")
            worklog_id = wl.get("id")

            # Only delete own worklogs
            if author_email.lower() != EMAIL.lower():
                continue

            # Parse timestamp
            try:
                started_dt = parse_jira_time(started_str)
                started_local = started_dt.astimezone(local_tz)
            except Exception as e:
                print(f"Failed to parse time for {worklog_id}: {e}")
                continue

            # Compare in IST (timezone-aware)
            if start_date <= started_local.replace(tzinfo=None) <= end_date:
                date_str = started_local.strftime("%Y-%m-%d %H:%M")
                print(f"Worklog {worklog_id} ({date_str} IST) by {display_name}")

                if dry_run:
                    print("Skipped (dry-run mode)\n")
                    continue

                status = delete_worklog(issue_id, worklog_id)
                if status == 204:
                    print("Deleted successfully\n")
                    deleted_count += 1
                else:
                    print(f"Failed ({status})\n")

        print(f"Total deleted in {issue_id}: {deleted_count}")
        total_deleted += deleted_count

    print("\n=====================================")
    print(f"Total worklogs deleted: {total_deleted}")
    print("Mode:", "Dry-run (no actual deletion)" if dry_run else "LIVE (deletions applied)")
    print("=====================================\n")


if __name__ == "__main__":
    main()
