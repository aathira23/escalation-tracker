"""
Email Service
Handles IMAP connections, email fetching, parsing, and processing.
"""
import email
import uuid
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_to_datetime

try:
    from imapclient import IMAPClient
except ImportError:
    IMAPClient = None

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EmailService:
    """Service for interacting with IMAP email servers."""
    
    @staticmethod
    def _decode_str(encoded_str: Any) -> str:
        """Decode email header strings."""
        if isinstance(encoded_str, bytes):
            return encoded_str.decode(errors='ignore')
        if not encoded_str:
            return ""
        
        decoded_list = decode_header(encoded_str)
        decoded_str = ""
        
        for content, encoding in decoded_list:
            if isinstance(content, bytes):
                if encoding:
                    try:
                        decoded_str += content.decode(encoding)
                    except (LookupError, UnicodeDecodeError):
                        decoded_str += content.decode('utf-8', errors='ignore')
                else:
                    decoded_str += content.decode('utf-8', errors='ignore')
            else:
                decoded_str += str(content)
                
        return decoded_str

    @staticmethod
    def connect() -> Optional[IMAPClient]:
        """Establish connection to IMAP server."""
        if not IMAPClient:
            logger.error("imapclient library not installed")
            return None
            
        if not all([settings.imap_server, settings.imap_email, settings.imap_password]):
            logger.warning("IMAP credentials not configured")
            return None
            
        try:
            client = IMAPClient(
                settings.imap_server, 
                port=settings.imap_port, 
                ssl=settings.imap_use_ssl
            )
            client.login(settings.imap_email, settings.imap_password)
            return client
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            return None

    @staticmethod
    def fetch_unread_emails(limit: int = 20) -> List[Dict]:
        """Fetch unread emails from the inbox."""
        client = EmailService.connect()
        if not client:
            return []
            
        emails = []
        
        try:
            # Select folder
            if not client.folder_exists(settings.imap_folder):
                logger.error(f"Folder {settings.imap_folder} does not exist")
                return []
                
            client.select_folder(settings.imap_folder)
            
            # Search for unread messages
            messages = client.search(['UNSEEN'])
            
            # Limit results
            messages = messages[:limit]
            
            if not messages:
                return []
                
            for uid, message_data in client.fetch(messages, ['RFC822', 'ENVELOPE']).items():
                try:
                    email_data = EmailService.parse_email(uid, message_data)
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error parsing email {uid}: {e}")
                    
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
        finally:
            try:
                client.logout()
            except:
                pass
                
        return emails

    @staticmethod
    def parse_email(uid: int, message_data: Dict) -> Optional[Dict]:
        """Parse raw email data into a structured dictionary."""
        try:
            envelope = message_data.get(b'ENVELOPE')
            
            # Helper to safely get envelope fields
            sender = ""
            if envelope and envelope.from_:
                mailbox = envelope.from_[0].mailbox.decode(errors='ignore') if envelope.from_[0].mailbox else ""
                host = envelope.from_[0].host.decode(errors='ignore') if envelope.from_[0].host else ""
                sender = f"{mailbox}@{host}"
                
            subject = ""
            if envelope and envelope.subject:
                subject = envelope.subject.decode(errors='ignore')
                
            # Date handling
            if envelope and envelope.date:
                received_at = envelope.date
            else:
                received_at = datetime.utcnow()

            # Parse Body using email library
            raw_content = message_data.get(b'RFC822')
            if not raw_content:
                return None
                
            msg = email.message_from_bytes(raw_content)
            
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode(errors='ignore')
                            break # Prefer plain text
                    elif content_type == "text/html" and not body:
                        # Fallback to HTML if no plain text found yet
                         payload = part.get_payload(decode=True)
                         if payload:
                             # Very basic strip tags could go here, but for now just raw text
                             body += payload.decode(errors='ignore')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors='ignore')
            
            # Generate ID based on Message-ID or random
            msg_id_header = msg.get("Message-ID")
            email_id = msg_id_header if msg_id_header else f"imap-{uid}-{uuid.uuid4()}"
            
            # Clean up body (basic)
            body = body.strip()
            
            # Parse Sender Name
            sender_name = None
            if envelope and envelope.from_ and envelope.from_[0].name:
                sender_name = envelope.from_[0].name.decode(errors='ignore')

            return {
                "uid": uid,
                "email_id": email_id,
                "sender_email": sender,
                "sender_name": sender_name,
                "subject": subject,
                "body": body,
                "received_at": received_at
            }
            
        except Exception as e:
            logger.error(f"Parser error: {e}")
            return None

    @staticmethod
    def mark_as_processed(uid: int, success: bool = True):
        """Mark email as processed or move to folder."""
        client = EmailService.connect()
        if not client:
            return
            
        try:
            client.select_folder(settings.imap_folder)
            
            # If we want to move to a processed folder
            if success and settings.imap_processed_folder:
                # Ensure folder exists
                if not client.folder_exists(settings.imap_processed_folder):
                    try:
                        client.create_folder(settings.imap_processed_folder)
                    except:
                        pass # Might fail if permissions issue
                
                if client.folder_exists(settings.imap_processed_folder):
                    client.move([uid], settings.imap_processed_folder)
                else:
                    # Fallback: just mark read
                    client.add_flags([uid], ['\\Seen'])
            else:
                # If failure, maybe mark as flagged/Seen?
                client.add_flags([uid], ['\\Seen'])
                
        except Exception as e:
            logger.error(f"Error marking email {uid}: {e}")
        finally:
            try:
                client.logout()
            except:
                pass
