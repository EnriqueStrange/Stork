import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "198Rl7s9Nznd7TtiFunyOoHLHEDXReX47zgurx4S81mA"

def main():
    credentials = None
    if os.path.exists("client_secret.json"):
        credentials= Credentials.from_authorized_user_file("client_secret.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expire and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()
        result = sheets.values().get(spreadsheetId = SPREADSHEET_ID, range="Sheet1!A1:C3").execute()
        values = result.get("values", [])

        for row in values:
            print(row)

    except HttpError as error:
        print(error)

    except:
        pass

if __name__ == "__main__":
    main()