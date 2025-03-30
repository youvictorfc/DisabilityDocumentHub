import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from flask import current_app

def send_form_email(recipient_email, form_title, pdf_path):
    """
    Send an email with a completed form PDF as an attachment.
    """
    try:
        # Get email configuration
        mail_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = int(os.environ.get('MAIL_PORT', 587))
        mail_use_tls = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
        mail_username = os.environ.get('MAIL_USERNAME')
        mail_password = os.environ.get('MAIL_PASSWORD')
        sender_email = os.environ.get('MAIL_DEFAULT_SENDER', mail_username)
        
        if not mail_username or not mail_password:
            raise Exception("Email credentials not configured")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Completed Form: {form_title}"
        
        # Email body
        body = f"""
        <html>
            <body>
                <h2>Completed Form Submission</h2>
                <p>Thank you for completing the form "{form_title}".</p>
                <p>Please find attached a PDF copy of your completed form.</p>
                <p>If you have any questions, please contact the Minto Disability Services team.</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Attach PDF
        with open(pdf_path, 'rb') as file:
            pdf_attachment = MIMEApplication(file.read(), _subtype='pdf')
        
        pdf_filename = os.path.basename(pdf_path)
        pdf_attachment.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
        msg.attach(pdf_attachment)
        
        # Send email
        with smtplib.SMTP(mail_server, mail_port) as server:
            if mail_use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        
        return True
    
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        raise Exception(f"Failed to send email: {str(e)}")
