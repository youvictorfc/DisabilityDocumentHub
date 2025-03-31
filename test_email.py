#!/usr/bin/env python3
import os
import sys
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Email configuration - from environment variables
config = {
    'mail_server': os.environ.get('MAIL_SERVER', 'smtp.gmail.com'),
    'mail_port': int(os.environ.get('MAIL_PORT', 587)),
    'mail_use_tls': os.environ.get('MAIL_USE_TLS', 'True') == 'True',
    'mail_use_ssl': os.environ.get('MAIL_USE_SSL', 'False') == 'True', 
    'mail_username': os.environ.get('MAIL_USERNAME'),
    'mail_password': os.environ.get('MAIL_PASSWORD'),
    'mail_default_sender': os.environ.get('MAIL_DEFAULT_SENDER')
}

# If no default sender, use username
if not config['mail_default_sender'] and config['mail_username']:
    config['mail_default_sender'] = config['mail_username']

# Email details
recipient_email = "youvictorfc@gmail.com"  # Valid email for testing
subject = "Email Test from Minto Disability Services"
body = """
<html>
    <body>
        <h2>Test Email</h2>
        <p>This is a test email from the Minto Disability Services Document Hub.</p>
        <p>If you're seeing this, the email configuration is working correctly.</p>
    </body>
</html>
"""

def send_test_email():
    """Send a test email to verify the configuration."""
    # Print configuration for debugging (hide password)
    safe_config = dict(config)
    if 'mail_password' in safe_config:
        safe_config['mail_password'] = '********'
    logger.info(f"Email configuration: {safe_config}")
    
    if not config['mail_username'] or not config['mail_password']:
        logger.error("Email credentials not configured.")
        return False
    
    try:
        # Create message
        logger.info(f"Creating email message to {recipient_email}")
        msg = MIMEMultipart()
        msg['From'] = config['mail_default_sender']
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        # Add a socket timeout to prevent hanging
        import socket
        socket.setdefaulttimeout(30)  # 30 seconds timeout
        
        # Connect to the server
        logger.info(f"Connecting to {config['mail_server']}:{config['mail_port']}")
        if config['mail_use_ssl']:
            logger.info("Using SSL")
            server = smtplib.SMTP_SSL(config['mail_server'], config['mail_port'])
        else:
            logger.info("Not using SSL")
            server = smtplib.SMTP(config['mail_server'], config['mail_port'])
            if config['mail_use_tls']:
                logger.info("Starting TLS")
                server.starttls()
        
        # Debug server communication
        server.set_debuglevel(1)
        
        # Login and send
        logger.info(f"Attempting to login with username: {config['mail_username']}")
        server.login(config['mail_username'], config['mail_password'])
        logger.info("Login successful")
        
        logger.info("Sending message")
        server.send_message(msg)
        logger.info("Message sent")
        
        server.quit()
        logger.info("Email sent successfully")
        return True
        
    except smtplib.SMTPAuthenticationError as auth_err:
        logger.error(f"SMTP Authentication Error: {str(auth_err)}")
        return False
        
    except smtplib.SMTPException as smtp_err:
        logger.error(f"SMTP Error: {str(smtp_err)}")
        return False
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    print("Sending test email...")
    success = send_test_email()
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email. Check the logs for details.")
        sys.exit(1)