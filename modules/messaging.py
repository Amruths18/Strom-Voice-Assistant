"""
Messaging Module for Strom AI Assistant
"""

import webbrowser
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional


class Messaging:
    """
    Manages WhatsApp and Email messaging.
    """
    
    def __init__(self, email_address: Optional[str] = None, email_password: Optional[str] = None):
        """Initialize messaging."""
        self.email_address = email_address
        self.email_password = email_password
        print("[Messaging] Initialized")
    
    def send_whatsapp(self, entities: Dict) -> str:
        """Send WhatsApp message."""
        recipient = entities.get('recipient', '').strip()
        message = entities.get('message', '').strip()
        
        if not recipient:
            return "Who should I send to?"
        
        if not message:
            return "What's the message?"
        
        try:
            encoded = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?text={encoded}"
            webbrowser.open(url)
            return f"Opening WhatsApp to send to {recipient}."
        except:
            return "Failed to open WhatsApp."
    
    def send_email(self, entities: Dict) -> str:
        """Send email."""
        recipient = entities.get('recipient', '').strip()
        message = entities.get('message', '').strip()
        
        if not recipient:
            return "Who should I email?"
        
        if not message:
            return "What's the message?"
        
        if not self.email_address or not self.email_password:
            return "Email not configured."
        
        if '@' not in recipient:
            return "Please provide a valid email address."
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient
            msg['Subject'] = "Message from Strom"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return f"Email sent to {recipient}."
        except:
            return "Failed to send email."