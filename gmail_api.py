from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
import requests
import re

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
PRIMER_API_KEY = 'Jkan5rpruBkmDajv_lll7beQ8xzhgzIM2gB7rhl_WZc'

def create_label(label: str, service: any):
    data = {'name': label}
    new_label = service.users().labels().create(userId='me', body=data).execute()
    print('created new label')
    return new_label.get('id')

def handle_label(label: str, service: any):

    labels = service.users().labels().list(userId='me').execute()

    if labels.get('labels'):
        
        for l in labels.get('labels'):
            if label == l['name']:
                return l['id']
        return create_label(label=label, service=service)
    else:
        return create_label(label=label, service=service)


def add_labels(message_id: str, labels: list, service: any):

    label_ids = list()

    for label in labels:
        label_id = handle_label(label=label, service=service)
        label_ids.append(label_id)

    data = {
        "addLabelIds": label_ids
    }

    service.users().messages().modify(userId='me', id=message_id, body=data).execute()



def strip_email(email: str):
    # wrapped links
    email = re.sub(r'\[.*\]\(.*\)', '', email)
    # leftover links
    email = re.sub(r'http\S+', '', email)
    # double newlines
    email = re.sub(r'\n\n', '', email)
    # double spaces
    email = re.sub(r'  ', '', email)
    return email


def get_sentiment(email: str):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {PRIMER_API_KEY}'
    }

    response = requests.post(
        url='https://engines.primer.ai/api/v1/classify/sentiment',
        headers=headers,
        json={'text': str(email)}
    )
    return response


def create_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def main():
    service = create_service()
    has_next_page = True
    next_page_token = None

    while has_next_page:
        if next_page_token:
            results = service.users().messages().list(
                userId='me', pageToken=next_page_token).execute()
        else:
            results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])
        next_page_token = results.get('nextPageToken')
        for message in messages:
            id = message['id']
            raw_message = service.users().messages().get(userId='me', id=id).execute()
            payload = raw_message.get('payload')
            mime_type = payload.get('mimeType')
            if mime_type == 'multipart/alternative':
                parts = payload.get('parts')
                for p in parts:
                    part_mime_type = p.get('mimeType')
                    if part_mime_type == 'text/plain':
                        plain_body = strip_email(base64.urlsafe_b64decode(
                            p.get('body').get('data')).decode('UTF-8'))
                        sentiment_response = get_sentiment(plain_body[:9999]).json()
                        if sentiment_response.get('sentiment'):
                            add_labels(message_id=id, labels=[sentiment_response.get('sentiment')], service=service)

        if next_page_token is None:
            has_next_page = False
        else:
            print(next_page_token)


if __name__ == '__main__':
    main()
