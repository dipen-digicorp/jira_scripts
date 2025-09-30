import os
import json
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Retrieve credentials
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
DOMAIN = os.getenv("JIRA_DOMAIN")

BASE_URL = f"https://{DOMAIN}/rest/api/3"
auth = HTTPBasicAuth(EMAIL, API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# # Test connection
# response = requests.get(f"{BASE_URL}/myself", headers=headers, auth=auth)
# if response.status_code == 200:
#     user = response.json()
#     print(f"Connected to Jira as {user['displayName']} ({user['emailAddress']})")
# else:
#     print("Failed to connect:", response.status_code, response.text)
#     exit(1)

issue_id = 14733  # SSC-12
author_name = "Dipen Motka"

# Convert start date to milliseconds since epoch
start_date = datetime(2025, 9, 1)
start_epoch_ms = int(start_date.timestamp() * 1000)

# Jira API URL with startedAfter filter
url = f"{BASE_URL}/issue/{issue_id}/worklog?startedAfter={start_epoch_ms}"

response = requests.get(url, headers=headers, auth=auth)

def extract_comment(comment_obj):
    """
    Converts Jira 'doc' comment structure into plain text.
    """
    try:
        content = comment_obj.get("content", [])
        texts = []
        for block in content:
            for c in block.get("content", []):
                texts.append(c.get("text", ""))
        return " ".join(texts)
    except:
        return ""

if response.status_code == 200:
    worklogs = response.json().get("worklogs", [])
    
    # Filter by author
    dipen_worklogs = [
        {
            "ID": w["id"],
            "Time Spent": w["timeSpent"],
            "Started": w["started"],
            "Comment": extract_comment(w.get("comment", {}))
        }
        for w in worklogs
        if w["author"]["displayName"] == author_name
    ]
    
    # Print results
    for w in dipen_worklogs:
        print(f"ID: {w['ID']}, Time Spent: {w['Time Spent']}, Started: {w['Started']}, Comment: {w['Comment']}")
else:
    print("Failed to fetch worklogs:", response.status_code, response.text)
