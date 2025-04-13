from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
from config import Config


class GmailService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/gmail.modify']
        self.service = self._build_service()

    def _build_service(self):
        creds = None
        token_path = 'token.json'

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GMAIL_CREDENTIALS_FILE, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def capture_draft(self, draft_id=None):
        try:
            if draft_id:
                draft = self.service.users().drafts().get(userId='me', id=draft_id).execute()
            else:
                drafts = self.service.users().drafts().list(userId='me').execute()
                draft = drafts['drafts'][0] if drafts.get('drafts') else None
                if not draft:
                    return None
                draft = self.service.users().drafts().get(userId='me', id=draft['id']).execute()

            message = draft['message']
            subject = next((header['value'] for header in message['payload']['headers'] if header['name'] == 'Subject'),
                           '')
            body = message.get('snippet', '')  # Simplified; in production, parse MIME parts

            return {
                'subject': subject,
                'content': body
            }
        except Exception as e:
            print(f"Error capturing draft: {e}")
            return None

    def update_draft(self, draft_id, new_content):
        draft = {
            'message': {
                'snippet': new_content,
                'payload': {'body': {'data': new_content}}  # Simplified
            }
        }
        self.service.users().drafts().update(userId='me', id=draft_id, body=draft).execute()