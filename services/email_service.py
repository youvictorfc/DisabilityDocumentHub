import os
import sys
import smtplib
import logging
import shutil
import socket
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from flask import current_app

# Import SendGrid if available
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
    import base64
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# Default Minto email address - used as the primary recipient for all form submissions
MINTO_DEFAULT_EMAIL = "hello@mintodisabilityservices.com.au"

class EmailManager:
    """Manages email sending operations with better error handling and fallback mechanisms."""
    
    def __init__(self, config=None):
        """Initialize with application config."""
        self.config = config or {}
        self.hardcoded_minto_email = MINTO_DEFAULT_EMAIL
        
    def get_email_config(self):
        """Get email configuration from environment variables or app config."""
        # First try to get from app config, then environment variables, then defaults
        config = {
            'mail_server': current_app.config.get('MAIL_SERVER', os.environ.get('MAIL_SERVER', 'smtp.gmail.com')),
            'mail_port': int(current_app.config.get('MAIL_PORT', os.environ.get('MAIL_PORT', 587))),
            'mail_use_tls': current_app.config.get('MAIL_USE_TLS', os.environ.get('MAIL_USE_TLS', 'True') == 'True'),
            'mail_use_ssl': current_app.config.get('MAIL_USE_SSL', os.environ.get('MAIL_USE_SSL', 'False') == 'True'),
            'mail_username': current_app.config.get('MAIL_USERNAME', os.environ.get('MAIL_USERNAME')),
            'mail_password': current_app.config.get('MAIL_PASSWORD', os.environ.get('MAIL_PASSWORD')),
            'mail_default_sender': current_app.config.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_DEFAULT_SENDER'))
        }
        
        # If no default sender, use username
        if not config['mail_default_sender'] and config['mail_username']:
            config['mail_default_sender'] = config['mail_username']
            
        return config
    
    def create_form_email(self, recipient_email, form_title, pdf_path, form_data=None):
        """Create an email message with the completed form attached."""
        # Get email configuration
        config = self.get_email_config()
        
        # Add multiple recipients
        recipients = [recipient_email]
        if self.hardcoded_minto_email.lower() != recipient_email.lower():
            recipients.append(self.hardcoded_minto_email)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = config['mail_default_sender'] or 'noreply@mintodisabilityservices.com.au'
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"Completed Form: {form_title}"
        
        # Create a more professional HTML email body
        body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h2 {{ color: #2a5885; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                    .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #eee; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Form Submission Confirmation</h2>
                    <p>Thank you for completing the <strong>{form_title}</strong> form.</p>
                    <p>Your submission has been received by Minto Disability Services and is being processed.</p>
                    <p>A PDF copy of your completed form is attached to this email for your records.</p>
                    
                    <div class="footer">
                        <p>If you have any questions, please contact the Minto Disability Services team.</p>
                        <p>This is an automated message from the Minto Disability Services Document Hub.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Attach PDF
        try:
            with open(pdf_path, 'rb') as file:
                pdf_attachment = MIMEApplication(file.read(), _subtype='pdf')
                
            pdf_filename = os.path.basename(pdf_path)
            pdf_attachment.add_header('Content-Disposition', f'attachment; filename={pdf_filename}')
            msg.attach(pdf_attachment)
            
        except Exception as e:
            current_app.logger.error(f"Error attaching PDF: {str(e)}")
            # Attach an error message instead
            error_text = f"Error attaching PDF: {str(e)}\nPDF path: {pdf_path}"
            error_attachment = MIMEText(error_text)
            error_attachment.add_header('Content-Disposition', 'attachment; filename="error_report.txt"')
            msg.attach(error_attachment)
        
        return msg, recipients, config
    
    def save_local_copy(self, recipient_email, form_title, pdf_path, form_data=None):
        """Save a local copy of the form submission when email sending fails."""
        try:
            # Create directories for local storage
            submitted_forms_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'submitted_forms')
            os.makedirs(submitted_forms_dir, exist_ok=True)
            
            # Create a subdirectory for this form
            form_dir = os.path.join(submitted_forms_dir, form_title.replace(' ', '_'))
            os.makedirs(form_dir, exist_ok=True)
            
            # Create a timestamped subdirectory for this submission
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            submission_dir = os.path.join(form_dir, f"{timestamp}")
            os.makedirs(submission_dir, exist_ok=True)
            
            # Copy the PDF
            new_pdf_path = os.path.join(submission_dir, os.path.basename(pdf_path))
            shutil.copy2(pdf_path, new_pdf_path)
            
            # Save submission metadata
            metadata = {
                "form_title": form_title,
                "recipient_email": recipient_email,
                "minto_email": self.hardcoded_minto_email,
                "timestamp": datetime.now().isoformat(),
                "pdf_path": new_pdf_path,
                "form_data": form_data
            }
            
            with open(os.path.join(submission_dir, "submission_metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            current_app.logger.info(f"Form submission saved locally to {submission_dir}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error saving local copy: {str(e)}")
            return False

def send_with_sendgrid(recipient_email, form_title, pdf_path, form_data=None):
    """
    Send an email with a completed form PDF as an attachment using SendGrid.
    
    Args:
        recipient_email (str): The email address of the recipient
        form_title (str): The title of the form
        pdf_path (str): The path to the PDF file to attach
        form_data (dict, optional): Additional form data for context
        
    Returns:
        dict: Result information including success status and message
    """
    if not SENDGRID_AVAILABLE:
        current_app.logger.warning("SendGrid not available. Install with 'pip install sendgrid'")
        return {
            'success': False,
            'method': 'error',
            'message': "SendGrid module not available."
        }
    
    # Check for SendGrid API key
    sendgrid_key = current_app.config.get('SENDGRID_API_KEY', os.environ.get('SENDGRID_API_KEY'))
    if not sendgrid_key:
        current_app.logger.warning("SendGrid API key not configured")
        return {
            'success': False,
            'method': 'error',
            'message': "SendGrid API key not configured."
        }
    
    current_app.logger.info(f"Sending form email with SendGrid for '{form_title}' to {recipient_email}")
    
    try:
        # Add the Minto email as a recipient
        recipients = [recipient_email]
        if MINTO_DEFAULT_EMAIL.lower() != recipient_email.lower():
            recipients.append(MINTO_DEFAULT_EMAIL)
        
        # Create mail message
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h2 {{ color: #2a5885; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                    .footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #eee; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Form Submission Confirmation</h2>
                    <p>Thank you for completing the <strong>{form_title}</strong> form.</p>
                    <p>Your submission has been received by Minto Disability Services and is being processed.</p>
                    <p>A PDF copy of your completed form is attached to this email for your records.</p>
                    
                    <div class="footer">
                        <p>If you have any questions, please contact the Minto Disability Services team.</p>
                        <p>This is an automated message from the Minto Disability Services Document Hub.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Create the message
        message = Mail(
            from_email=Email('noreply@mintodisabilityservices.com.au'),
            to_emails=[To(r) for r in recipients],
            subject=f"Completed Form: {form_title}",
            html_content=Content("text/html", html_content)
        )
        
        # Attach the PDF
        try:
            with open(pdf_path, 'rb') as f:
                pdf_data = f.read()
                
            encoded_pdf = base64.b64encode(pdf_data).decode()
            pdf_filename = os.path.basename(pdf_path)
            
            attachment = Attachment()
            attachment.file_content = FileContent(encoded_pdf)
            attachment.file_name = FileName(pdf_filename)
            attachment.file_type = FileType('application/pdf')
            attachment.disposition = Disposition('attachment')
            message.attachment = attachment
            
        except Exception as e:
            current_app.logger.error(f"Error attaching PDF with SendGrid: {str(e)}")
            # Continue without attachment
        
        # Send the email
        sg = SendGridAPIClient(sendgrid_key)
        response = sg.send(message)
        
        # Log the response
        current_app.logger.info(f"SendGrid response status code: {response.status_code}")
        
        if response.status_code >= 200 and response.status_code < 300:
            current_app.logger.info(f"Email sent successfully with SendGrid to {', '.join(recipients)}")
            return {
                'success': True,
                'method': 'sendgrid',
                'recipients': recipients,
                'message': "Email sent successfully with SendGrid"
            }
        else:
            current_app.logger.error(f"SendGrid error: Status code {response.status_code}")
            return {
                'success': False,
                'method': 'sendgrid_error',
                'error': f"SendGrid error: Status code {response.status_code}",
                'message': "Email sending failed with SendGrid. Form was saved locally."
            }
            
    except Exception as e:
        current_app.logger.error(f"SendGrid error: {str(e)}")
        return {
            'success': False,
            'method': 'sendgrid_error',
            'error': str(e),
            'message': "Error sending email with SendGrid. Form was saved locally."
        }

def send_form_email(recipient_email, form_title, pdf_path, form_data=None):
    """
    Send an email with a completed form PDF as an attachment.
    If email credentials are not available or sending fails, save a copy locally.
    
    Args:
        recipient_email (str): The email address of the recipient
        form_title (str): The title of the form
        pdf_path (str): The path to the PDF file to attach
        form_data (dict, optional): Additional form data for context
        
    Returns:
        dict: Result information including success status and message
    """
    current_app.logger.info(f"Sending form email for '{form_title}' to {recipient_email}")
    
    # Initialize email manager
    email_manager = EmailManager()
    
    # First, always save a local copy as backup
    email_manager.save_local_copy(recipient_email, form_title, pdf_path, form_data)
    
    # Try SendGrid first if available
    sendgrid_key = current_app.config.get('SENDGRID_API_KEY', os.environ.get('SENDGRID_API_KEY'))
    if SENDGRID_AVAILABLE and sendgrid_key:
        current_app.logger.info("Attempting to send email with SendGrid")
        result = send_with_sendgrid(recipient_email, form_title, pdf_path, form_data)
        if result['success']:
            return result
        else:
            current_app.logger.warning("SendGrid failed, falling back to SMTP")
    
    try:
        # Create the email message
        msg, recipients, config = email_manager.create_form_email(recipient_email, form_title, pdf_path, form_data)
        
        # Check if we have email credentials
        if not config['mail_username'] or not config['mail_password']:
            current_app.logger.warning("Email credentials not configured. Form saved locally only.")
            return {
                'success': False,
                'method': 'local',
                'message': "Email credentials not configured. Form saved locally."
            }
        
        # Try to send the email
        try:
            # Add a socket timeout to prevent hanging
            socket.setdefaulttimeout(30)  # 30 seconds timeout
            
            # Connect to server
            if config['mail_use_ssl']:
                server = smtplib.SMTP_SSL(config['mail_server'], config['mail_port'])
            else:
                server = smtplib.SMTP(config['mail_server'], config['mail_port'])
                if config['mail_use_tls']:
                    server.starttls()
            
            # Login and send
            # More detailed logging for debugging
            current_app.logger.info(f"Attempting to login with username: {config['mail_username']}")
            current_app.logger.info(f"Mail server: {config['mail_server']}, port: {config['mail_port']}, TLS: {config['mail_use_tls']}")
            
            try:
                server.login(config['mail_username'], config['mail_password'])
                current_app.logger.info("Login successful")
                
                server.send_message(msg)
                current_app.logger.info("Message sent")
                
                server.quit()
                current_app.logger.info(f"Email sent successfully to {', '.join(recipients)}")
                
                return {
                    'success': True,
                    'method': 'email',
                    'recipients': recipients,
                    'message': "Email sent successfully"
                }
            except smtplib.SMTPAuthenticationError as auth_err:
                error_str = str(auth_err)
                current_app.logger.error(f"SMTP Authentication Error: {error_str}")
                
                # Special handling for Gmail's app-specific password requirement
                if "Application-specific password required" in error_str:
                    message = ("Gmail requires an App-specific password when 2FA is enabled. "
                              "Please visit https://myaccount.google.com/apppasswords to generate one. "
                              "Form was saved locally.")
                    current_app.logger.warning("Gmail app-specific password required")
                else:
                    message = "Email sending failed due to authentication error. Form was saved locally."
                
                return {
                    'success': False,
                    'method': 'local',
                    'error': f"Authentication failed: {error_str}",
                    'message': message
                }
            except smtplib.SMTPException as smtp_err:
                current_app.logger.error(f"SMTP Error: {str(smtp_err)}")
                return {
                    'success': False,
                    'method': 'local',
                    'error': f"SMTP error: {str(smtp_err)}",
                    'message': "Email sending failed due to SMTP error. Form was saved locally."
                }
            
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            current_app.logger.info("Email sending failed, but form was saved locally")
            
            return {
                'success': False,
                'method': 'local',
                'error': str(e),
                'message': "Email sending failed, but form was saved locally"
            }
    
    except Exception as e:
        current_app.logger.error(f"Error preparing email: {str(e)}")
        
        return {
            'success': False,
            'method': 'error',
            'error': str(e),
            'message': "Error preparing email, but form was saved locally"
        }
