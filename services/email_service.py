import os
import smtplib
import logging
import shutil
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from flask import current_app

def send_form_email(recipient_email, form_title, pdf_path):
    """
    Send an email with a completed form PDF as an attachment.
    If email credentials are not available, save a copy to a local directory.
    """
    try:
        # Set the hardcoded email for Minto Disability Services
        minto_email = "hello@mintodisabilityservices.com.au"
        
        # Get email configuration from environment variables
        mail_server = current_app.config.get('MAIL_SERVER', os.environ.get('MAIL_SERVER', 'smtp.gmail.com'))
        mail_port = int(current_app.config.get('MAIL_PORT', os.environ.get('MAIL_PORT', 587)))
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', os.environ.get('MAIL_USE_TLS', 'True') == 'True')
        mail_username = current_app.config.get('MAIL_USERNAME', os.environ.get('MAIL_USERNAME'))
        mail_password = current_app.config.get('MAIL_PASSWORD', os.environ.get('MAIL_PASSWORD'))
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_DEFAULT_SENDER', mail_username))
        
        # Add the Minto email to recipients if not already included
        recipients = [recipient_email]
        if minto_email.lower() != recipient_email.lower():
            recipients.append(minto_email)
        
        # Try to send email if we have credentials
        if mail_username and mail_password:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ", ".join(recipients)
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
            
            current_app.logger.info(f"Email sent successfully to {', '.join(recipients)}")
            return True
        
        # If we don't have email credentials, save a copy to a local directory
        else:
            current_app.logger.warning("Email credentials not configured. Saving form locally instead.")
            
            # Create a directory for submitted forms if it doesn't exist
            submitted_forms_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'submitted_forms')
            os.makedirs(submitted_forms_dir, exist_ok=True)
            
            # Create a subdirectory for the recipient's email
            recipient_dir = os.path.join(submitted_forms_dir, minto_email.replace('@', '_at_'))
            os.makedirs(recipient_dir, exist_ok=True)
            
            # Copy the PDF to the recipient's directory with a timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{os.path.basename(pdf_path)}"
            new_path = os.path.join(recipient_dir, new_filename)
            
            shutil.copy2(pdf_path, new_path)
            
            # Create a text file with submission details
            info_file = os.path.join(recipient_dir, f"{timestamp}_submission_info.txt")
            with open(info_file, 'w') as f:
                f.write(f"Form Title: {form_title}\n")
                f.write(f"Submitted At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Recipient Email: {recipient_email}\n")
                f.write(f"Minto Email: {minto_email}\n")
                f.write(f"PDF Path: {new_path}\n")
            
            current_app.logger.info(f"Form submission saved locally to {new_path}")
            return True
    
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        raise Exception(f"Failed to send email: {str(e)}")
