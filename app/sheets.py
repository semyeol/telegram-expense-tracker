import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds_json = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
creds = service_account.Credentials.from_service_account_info(
    creds_json, 
    scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ],
)

# build the APIs
drive_service = build("drive", "v3", credentials=creds)
sheets_service = build("drive", "v3", credentials=creds)


    
def create_new_sheet():
    pass

def append_transaction():
    pass


# check if "Expense Tracker {year}"" exists
# if yes, append transaction in correct month sheet based on telegram msg date (use backend datetime as fallback)
# if no, duplicate "Expense Tracker MASTER" and rename