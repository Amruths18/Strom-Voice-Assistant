"""
Messaging Module for Strom AI Assistant
Handles WhatsApp and email message sending.
Requires online connectivity and proper authentication.
"""

import webbrowser
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import os


class Messaging:
    """
    Manages messaging operations for WhatsApp and Email.
    Requires online connectivity for operation.
    """
    
    def __init__(
        self,
        email_address: Optional[str] = None,
        email_password: Optional[str] = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587
    ):
        """
        Initialize messaging module.
        
        Args:
            email_address: Sender's email address
            email_password: Sender's email password (app password for Gmail)
            smtp_server: SMTP server address
            smtp_port: SMTP server port
        """
        self.email_address = email_address or os.getenv('STROM_EMAIL')
        self.email_password = email_password or os.getenv('STROM_EMAIL_PASSWORD')
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
        print("[Messaging] Messaging module initialized.")
        
        if not self.email_address:
            print("[Messaging] WARNING: No email configured. Email features will be limited.")
    
    def send_whatsapp(self, entities: Dict) -> str:
        """
        Send WhatsApp message using WhatsApp Web.
        Opens browser with pre-filled message.
        
        Args:
            entities: Must contain 'recipient' and optionally 'message'
            
        Returns:
            Status message
        """
        recipient = entities.get('recipient', '').strip()
        message = entities.get('message', '').strip()
        
        if not recipient:
            return "Please specify the recipient's name or number."
        
        if not message:
            return "Please specify the message to send."
        
        try:
            # Format message for URL
            encoded_message = urllib.parse.quote(message)
            
            # Try with phone number format first
            # Note: In production, you'd want a contact mapping system
            if recipient.isdigit():
                # Direct phone number
                url = f"https://web.whatsapp.com/send?phone={recipient}&text={encoded_message}"
            else:
                # Search by name (opens chat selection)
                url = f"https://web.whatsapp.com/send?text={encoded_message}"
            
            # Open WhatsApp Web
            webbrowser.open(url)
            
            return f"Opening WhatsApp to send message to {recipient}. Please confirm and send."
            
        except Exception as e:
            return f"Failed to open WhatsApp: {str(e)}"
    
    def send_email(self, entities: Dict) -> str:
        """
        Send email message.
        
        Args:
            entities: Must contain 'recipient' and 'message', optionally 'subject'
            
        Returns:
            Status message
        """
        recipient = entities.get('recipient', '').strip()
        message = entities.get('message', '').strip()
        subject = entities.get('subject', 'Message from Strom AI Assistant')
        
        if not recipient:
            return "Please specify the recipient's email address."
        
        if not message:
            return "Please specify the message to send."
        
        # Validate email configuration
        if not self.email_address or not self.email_password:
            return "Email is not configured. Please set up email credentials in config/api.yaml"
        
        # Add email domain if not present
        if '@' not in recipient:
            return f"Please provide a valid email address for {recipient}."
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Attach message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Connect to SMTP server
            print(f"[Messaging] Connecting to {self.smtp_server}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Login
            server.login(self.email_address, self.email_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            return f"Email sent to {recipient}."
            
        except smtplib.SMTPAuthenticationError:
            return "Email authentication failed. Please check your credentials."
        except smtplib.SMTPException as e:
            return f"Failed to send email: {str(e)}"
        except Exception as e:
            return f"Error sending email: {str(e)}"
    
    def get_contact_email(self, name: str) -> Optional[str]:
        """
        Get email address from contact name.
        In production, this would query a contacts database.
        
        Args:
            name: Contact name
            
        Returns:
            Email address or None
        """
        # Placeholder for contact mapping
        # In production, implement proper contact management
        contacts = {
            'john': 'john@example.com',
            'jane': 'jane@example.com',
            'mom': 'mom@example.com'
        }
        
        return contacts.get(name.lower())
    
    def get_contact_phone(self, name: str) -> Optional[str]:
        """
        Get phone number from contact name.
        In production, this would query a contacts database.
        
        Args:
            name: Contact name
            
        Returns:
            Phone number or None
        """
        # Placeholder for contact mapping
        # In production, implement proper contact management
        contacts = {
            'john': '+1234567890',
            'jane': '+0987654321',
            'mom': '+1122334455'
        }
        
        return contacts.get(name.lower())


# Test function
def _test_messaging():
    """Test messaging module functionality."""
    
    print("=== Strom Messaging Module Test ===\n")
    
    messaging = Messaging()
    
    # Test WhatsApp (will open browser)
    print("Test 1: WhatsApp Message")
    result = messaging.send_whatsapp({
        'recipient': 'John',
        'message': 'Hello from Strom AI!'
    })
    print(f"Result: {result}\n")
    
    # Test Email (requires configuration)
    print("Test 2: Email Message")
    result = messaging.send_email({
        'recipient': 'test@example.com',
        'message': 'This is a test email from Strom AI Assistant.',
        'subject': 'Test Email'
    })
    print(f"Result: {result}\n")


if __name__ == "__main__":
    _test_messaging()