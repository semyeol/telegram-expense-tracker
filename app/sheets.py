import os
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds_json = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
creds = service_account.Credentials.from_service_account_info(
    creds_json,
    scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

# build the APIs
drive_service = build("drive", "v3", credentials=creds)
sheets_service = build("sheets", "v4", credentials=creds)


def convert_timestamp(timestamp):
    dt = datetime.fromtimestamp(
        timestamp, tz=timezone.utc
    )  # convert from telegram's unix to UTC
    local_time = dt.astimezone(
        ZoneInfo("America/Los_Angeles")
    )  # convert to PST, still a datetime object
    # local_time = local_time.strftime("%Y-%m-%d %H:%M:%S") # string
    year = local_time.year

    return local_time, year

# find spreadsheet in Drive, reuseable
def find_file(name):
    response = (
          drive_service.files()
          .list(
              q=f"name = '{name}'",
              fields="files(id, name)",
              spaces="drive"
          )
          .execute()
      )

    files = response.get('files', [])
    if files:
        return files[0]['id']
    else:
        return None

def get_spreadsheet(timestamp):
    _, year = convert_timestamp(timestamp)
    spreadsheet_name = f"Expense Tracker {year}" # construct full file name
    file_id = find_file(spreadsheet_name)

    if file_id:
        return file_id
    else:
        return None

def create_speadsheet(year):
    # search for "Expense Tracker Template", get file id
    # duplicate the template, rename it, get the new file id
    template_id = find_file('Expense Tracker Template')
    if not template_id:
        raise FileNotFoundError("Template file was not found")
    
    try:
        new_file_name = f"Expense Track {year}"
        response = drive_service.files().copy(
            fileId=template_id,
            body={"name": new_file_name}
        ).execute()

        return response['id']
    except Exception as e: # any error
        raise Exception(f"Failed to create spreadsheet for {year}: {e}")

def append_transaction():
    pass

