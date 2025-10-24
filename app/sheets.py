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
    year = local_time.year
    month = local_time.month
    day = local_time.day

    return local_time, year, month, day

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
    _, year, _, _ = convert_timestamp(timestamp)
    spreadsheet_name = f"Expense Tracker {year}"
    spreadsheet_id = find_file(spreadsheet_name)

    if spreadsheet_id:
        return spreadsheet_id
    else:
        return create_spreadsheet(year)

def create_spreadsheet(year):
    # search for "Expense Tracker Template", get file id
    # duplicate the template, rename it, get the new file id
    template_id = find_file('Expense Tracker Template')
    if not template_id:
        print("Template file was not found.")
        raise FileNotFoundError("Template file was not found.") # raise for system issues
    
    try:
        new_spreadsheet_name = f"Expense Track {year}"
        response = drive_service.files().copy(
            fileId=template_id,
            body={"name": new_spreadsheet_name}
        ).execute()

        return response['id']
    except Exception as e: # any error
        print("Failed to create spreadsheet.")
        raise Exception(f"Failed to create spreadsheet for {year}: {e}")

def append_transaction(spreadsheet_id, timestamp, parsed_data):
    # only append if confident in answer
    confidence = parsed_data.get("confidence", 0)
    if confidence <= 0.90:
        return False # boolean for data issues

    local_time, year, month, day = convert_timestamp(timestamp)
    date_str = local_time.strftime("%Y-%m-%d")
    month_abbr = local_time.strftime("%b").upper()  # match sheet naming: "JAN" "FEB"

    # table format is: [description, category, amount, date, from]
    row = [
        parsed_data["description"],
        parsed_data["category"],
        parsed_data["amount"],
        date_str,
        "Work" 
    ]

    range_str = f"{month_abbr}!D:H"

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_str,
            valueInputOption="USER_ENTERED",
            body={"values": [row]}
        ).execute()

        return True  
    except Exception as e:
        print(f"Error appending transaction: {e}")
        return False  

def undo():
    pass