import base64
import re
import email
from email.mime.text import MIMEText

class EmailCapture:
    """
    Module responsible for capturing and parsing email drafts from Gmail.
    """
    
    def __init__(self, gmail_api):
        """
        Initialize the EmailCapture module.
        
        Args:
            gmail_api: An instance of the GmailAPI utility class
        """
        self.gmail_api = gmail_api
    
    def capture_draft(self, draft_id):
        """
        Captures email data from a Gmail draft.
        
        Args:
            draft_id: The ID of the Gmail draft
            
        Returns:
            A dictionary containing the email's subject and content
        """
        try:
            # Get draft from Gmail API
            draft = self.gmail_api.get_draft(draft_id)
            if not draft:
                return None
            
            # Extract raw message
            message = draft.get('message', {})
            raw_message = message.get('raw', '')
            
            if not raw_message:
                return self._extract_from_payload(message)
            
            # Decode raw message
            decoded_message = base64.urlsafe_b64decode(raw_message).decode('utf-8')
            mime_message = email.message_from_string(decoded_message)
            
            # Extract subject and content
            subject = mime_message.get('Subject', '')
            
            # Get content from the email body
            content = ''
            if mime_message.is_multipart():
                for part in mime_message.get_payload():
                    if part.get_content_type() == 'text/plain':
                        content = part.get_payload(decode=True).decode('utf-8')
                        break
            else:
                content = mime_message.get_payload(decode=True).decode('utf-8')
            
            return {
                'subject': subject,
                'content': content
            }
            
        except Exception as e:
            print(f"Error capturing draft: {e}")
            return None
    
    def _extract_from_payload(self, message):
        """
        Extract email data from message payload (alternative method).
        
        Args:
            message: The message object from Gmail API
            
        Returns:
            A dictionary containing the email's subject and content
        """
        try:
            # Get payload from message
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract subject from headers
            subject = ''
            for header in headers:
                if header.get('name', '').lower() == 'subject':
                    subject = header.get('value', '')
                    break
            
            # Extract content from payload parts
            content = ''
            parts = payload.get('parts', [])
            
            if parts:
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            content = base64.urlsafe_b64decode(body_data).decode('utf-8')
                            break
            else:
                # Try to get content from body directly
                body_data = payload.get('body', {}).get('data', '')
                if body_data:
                    content = base64.urlsafe_b64decode(body_data).decode('utf-8')
            
            return {
                'subject': subject,
                'content': content
            }
            
        except Exception as e:
            print(f"Error extracting from payload: {e}")
            return None
    
    def update_draft(self, draft_id, subject, content):
        """
        Updates an existing Gmail draft with new content.
        
        Args:
            draft_id: The ID of the Gmail draft
            subject: The updated subject
            content: The updated content
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Create a new MIMEText message
            message = MIMEText(content)
            message['Subject'] = subject
            message['To'] = ''  # Gmail requires this field but we can leave it empty for drafts
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8')).decode('utf-8')
            
            # Update the draft via Gmail API
            success = self.gmail_api.update_draft(draft_id, raw_message)
            
            return success
            
        except Exception as e:
            print(f"Error updating draft: {e}")
            return False