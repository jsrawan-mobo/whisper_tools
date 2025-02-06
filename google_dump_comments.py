from __future__ import print_function
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.readonly']

def list_shared_drives(service):
    """Lists all Shared Drives and prints their names and IDs."""
    page_token = None
    print("Shared Drives:")
    while True:
        response = service.drives().list(
            pageSize=100,  # Adjust the page size if needed
            pageToken=page_token,
            fields="nextPageToken, drives(id, name)",
        ).execute()

        drives = response.get('drives', [])
        if not drives:
            print("No Shared Drives found.")
            return

        for drive in drives:
            print("Name: {0}, ID: {1}".format(drive.get('name'), drive.get('id')))

        page_token = response.get('nextPageToken', None)
        if not page_token:
            break


def main():
    """Shows basic usage of the Drive v3 API.
    Lists the names and IDs of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This will open a browser window for you to log in.
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the Drive service.
    service = build('drive', 'v3', credentials=creds)

    list_shared_drives(service)

    shared_drive_id = '0AKsYb91iiQ5SUk9PVA' #Hfunds Marketing
    folder_id = ''  # For example, the folder you want to list files from

    # You can set up a query to list files that are within a specific folder.
    # The query "'<folder_id>' in parents" will list files whose parent is that folder.
    query = f"'{folder_id}' in parents"

    page_token = None
    while True:
        response = service.files().list(
            corpora='drive',  # Querying within a Shared Drive
            driveId=shared_drive_id,  # Specify the Shared Drive ID
            includeItemsFromAllDrives=True,  # Include files from shared drives
            supportsAllDrives=True,  # Ensure the API call supports shared drives
            q=query,  # Filter by the parent folder
            fields="nextPageToken, files(id, name)",
            pageToken=page_token,
            pageSize=100  # Adjust page size as needed
        ).execute()

        items = response.get('files', [])
        if not items:
            print('No files found in the specified folder.')
        else:
            for item in items:
                print(f"Name: {item.get('name')}, ID: {item.get('id')}")

        page_token = response.get('nextPageToken')
        if not page_token:
            break


    # # Call the Drive v3 API to list files.
    # results = service.files().list(
    #     pageSize=10,  # Change this value to list more files.
    #     fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])
    #
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()
