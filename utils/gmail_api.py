from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText
import json

class GmailAPI:
    """
    Utility class for interacting with the Gmail API.
    """
    
    def __init__(self, credentials):
        """
        Initialize the GmailAPI utility.
        
        Args:
            credentials: Google OAuth2 credentials
        """
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def get_drafts(self):
        """
        Get a list of all drafts.
        
        Returns:
            A list of draft objects
        """
        try:
            results = self.service.users().drafts().list(userId='me').execute()
            drafts = results.get('drafts', [])
            return drafts
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def get_draft(self, draft_id):
        """
        Get a specific draft by ID.
        
        Args:
            draft_id: The ID of the draft
            
        Returns:
            The draft object
        """
        try:
            draft = self.service.users().drafts().get(userId='me', id=draft_id).execute()
            return draft
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def create_draft(self, message_body):
        """
        Create a new draft.
        
        Args:
            message_body: The body of the message
            
        Returns:
            The created draft object
        """
        try:
            message = MIMEText(message_body)
            message['To'] = ''  # Recipient can be set later
            message['Subject'] = ''  # Subject can be set later
            
            raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')
            draft = {'message': {'raw': raw_message}}
            
            created_draft = self.service.users().drafts().create(userId='me', body=draft).execute()
            return created_draft
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def update_draft(self, draft_id, raw_message):
        """
        Update an existing draft.
        
        Args:
            draft_id: The ID of the draft to update
            raw_message: The raw message data
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            draft = {'message': {'raw': raw_message}}
            
            updated_draft = self.service.users().drafts().update(
                userId='me', 
                id=draft_id,
                body=draft
            ).execute()
            
            return True if updated_draft else False
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
    
    def delete_draft(self, draft_id):
        """
        Delete a draft.
        
        Args:
            draft_id: The ID of the draft to delete
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        try:
            self.service.users().drafts().delete(userId='me', id=draft_id).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
    
    def send_draft(self, draft_id):
        """
        Send a draft.
        
        Args:
            draft_id: The ID of the draft to send
            
        Returns:
            The sent message ID if successful, None otherwise
        """
        try:
            sent_message = self.service.users().drafts().send(
                userId='me',
                body={'id': draft_id}
            ).execute()
            return sent_message.get('id')
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None