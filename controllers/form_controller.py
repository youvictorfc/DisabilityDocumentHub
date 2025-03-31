import json
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Form, FormResponse
from services.form.form_service import extract_form_structure, validate_form_submission
from services.form.pdf_service import generate_pdf_from_form
from services.email_service import send_form_email

form_bp = Blueprint('form', __name__, url_prefix='/forms')

@form_bp.route('/')
@login_required
def form_list():
    forms = Form.query.all()
    
    # Get user's in-progress forms
    user_responses = FormResponse.query.filter_by(
        user_id=current_user.id,
        is_complete=False
    ).all()
    
    in_progress_forms = []
    for response in user_responses:
        in_progress_forms.append({
            'form_id': response.form_id,
            'form_title': response.form.title,
            'response_id': response.id,
            'updated_at': response.updated_at
        })
    
    return render_template('forms/form_list.html', forms=forms, in_progress_forms=in_progress_forms)

@form_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_form():
    if not current_user.is_admin:
        flash('Only administrators can upload forms', 'danger')
        return redirect(url_for('form.form_list'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('form_file')
        
        if not title or not file:
            flash('Title and form file are required', 'danger')
            return render_template('forms/form_upload.html')
        
        # Check file extension
        if file.filename == '':
            flash('No file selected', 'danger')
            return render_template('forms/form_upload.html')
        
        # Allow a specific set of file types - restrict to ones that work well with OpenAI
        supported_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'txt', 'doc', 'docx'}
        file_extension = ''
        
        if '.' in file.filename:
            file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        if not file_extension or file_extension not in supported_extensions:
            flash(f'File type "{file_extension}" not supported. Please use PDF, JPG, PNG, GIF, or TXT formats.', 'danger')
            return render_template('forms/form_upload.html')
            
        # Check file size - OpenAI has limits (typically ~20-25MB)
        max_size_mb = 20
        if file.content_length and file.content_length > max_size_mb * 1024 * 1024:
            file_size_mb = file.content_length / (1024 * 1024)
            flash(f'File too large ({file_size_mb:.1f} MB). Maximum size is {max_size_mb} MB.', 'danger')
            return render_template('forms/form_upload.html')
        
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['FORM_UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Make sure upload directory exists
        os.makedirs(current_app.config['FORM_UPLOAD_FOLDER'], exist_ok=True)
        
        # Variable to hold form structure
        form_structure = None
        questions_count = 0
        
        try:
            # Flag to track if we should use OpenAI extraction
            use_openai_extraction = True
            
            # Special case for the Incident Form
            if "incident" in filename.lower() or (file_extension.lower() in ["docx"] and filename.lower().find("incident") != -1):
                current_app.logger.info("Detected an incident form upload, checking if we should use specialized template")
                # Import directly here to avoid circular imports
                from services.form.incident_form_template import get_incident_form_template, is_incident_form
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using incident form template for .docx file")
                    form_structure = {
                        "questions": get_incident_form_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using incident form template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like an incident form
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_incident_form(content):
                            current_app.logger.info("Detected incident form content, using specialized template")
                            form_structure = {
                                "questions": get_incident_form_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using incident form template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not an incident form or couldn't extract content, proceed to normal extraction
                            current_app.logger.info("Content doesn't appear to be an incident form, proceeding with normal extraction")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is an incident form: {str(e)}")
            
            # Use OpenAI extraction if we haven't already used a template
            if use_openai_extraction:
                # Extract form structure using OpenAI - preserve EXACT questions and order
                current_app.logger.info(f"Extracting EXACT form structure from {file_path}")
                
                try:
                    # Extract the form structure
                    form_structure = extract_form_structure(file_path)
                    
                    # Log the extracted structure for debugging
                    current_app.logger.debug(f"Extracted form structure: {json.dumps(form_structure)[:500]}...")
                    
                    # Validate the extracted structure
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Successfully extracted {questions_count} questions in their exact original form")
                    
                    # Check if we have a reasonable number of questions
                    if questions_count == 0:
                        raise ValueError("No questions could be extracted from the form document. Please try a different file or format.")
                    
                    # Check that questions have required fields
                    missing_fields = []
                    for i, question in enumerate(form_structure.get('questions', [])):
                        if not question.get('question_text') and not question.get('question') and not question.get('label'):
                            missing_fields.append(f"Question #{i+1} is missing required text field")
                        if not question.get('id'):
                            missing_fields.append(f"Question #{i+1} is missing a required ID")
                    
                    if missing_fields:
                        raise ValueError(f"Form structure validation failed: {'. '.join(missing_fields)}")
                
                except Exception as extraction_error:
                    current_app.logger.error(f"Form extraction error: {str(extraction_error)}")
                    flash(f'Error extracting form: {str(extraction_error)}', 'danger')
                    
                    # Clean up the file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return render_template('forms/form_upload.html')
            
            # Create form record with additional metadata
            new_form = Form(
                title=title,
                description=description,
                file_path=file_path,
                structure=json.dumps(form_structure),
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_form)
            db.session.commit()
            
            # Provide detailed success feedback
            flash(f'Form "{title}" uploaded successfully with {questions_count} questions extracted.', 'success')
            current_app.logger.info(f"Form ID {new_form.id} saved to database with {questions_count} questions")
            
            return redirect(url_for('form.form_list'))
            
        except Exception as e:
            current_app.logger.error(f"Error processing form: {str(e)}")
            flash(f'Error processing form: {str(e)}', 'danger')
            
            # Clean up the file on error
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    current_app.logger.info(f"Cleaned up file {file_path} after error")
                except Exception as cleanup_error:
                    current_app.logger.error(f"Error cleaning up file: {str(cleanup_error)}")
            
            return render_template('forms/form_upload.html')
    
    return render_template('forms/form_upload.html')

@form_bp.route('/<int:form_id>/fill', methods=['GET'])
@login_required
def fill_form(form_id):
    form = Form.query.get_or_404(form_id)
    
    # Check if there's an existing in-progress response
    existing_response = FormResponse.query.filter_by(
        form_id=form_id,
        user_id=current_user.id,
        is_complete=False
    ).first()
    
    # Always use full form view (step-by-step view has been removed per client request)
    
    if existing_response:
        response = existing_response
        form_structure = json.loads(form.structure)
        current_answers = json.loads(existing_response.answers) if existing_response.answers else {}
    else:
        # Create new form response
        new_response = FormResponse(
            form_id=form_id,
            user_id=current_user.id,
            answers=json.dumps({})
        )
        db.session.add(new_response)
        db.session.commit()
        
        response = new_response
        form_structure = json.loads(form.structure)
        current_answers = {}
    
    # Show all questions at once in the full form view
    return render_template('forms/form_fill.html', 
                          form=form, 
                          form_data=form_structure, 
                          answers=current_answers, 
                          response_id=response.id)

@form_bp.route('/response/<int:response_id>/save', methods=['POST'])
@login_required
def save_form_progress(response_id):
    response = FormResponse.query.get_or_404(response_id)
    
    # Ensure user owns this response
    if response.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json
    answers = data.get('answers', {})
    
    # Update response
    response.answers = json.dumps(answers)
    response.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@form_bp.route('/response/<int:response_id>/submit', methods=['POST'])
@login_required
def submit_form(response_id):
    response = FormResponse.query.get_or_404(response_id)
    
    # Ensure user owns this response
    if response.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    form = Form.query.get(response.form_id)
    data = request.json
    answers = data.get('answers', {})
    
    # Validate submission
    form_structure = json.loads(form.structure)
    validation_result = validate_form_submission(form_structure, answers)
    
    if not validation_result['valid']:
        return jsonify({
            'success': False, 
            'message': 'Form has incomplete or invalid fields',
            'missing_fields': validation_result['missing_fields']
        }), 400
    
    # Generate PDF with better error handling
    try:
        # Ensure the PDF output directory exists
        os.makedirs(current_app.config['PDF_OUTPUT_FOLDER'], exist_ok=True)
        
        # Create a descriptive filename with form title, user info, and timestamp
        safe_title = secure_filename(form.title)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        pdf_filename = f"{safe_title}_form{form.id}_user{current_user.id}_{timestamp}.pdf"
        pdf_path = os.path.join(current_app.config['PDF_OUTPUT_FOLDER'], pdf_filename)
        
        current_app.logger.info(f"Generating PDF for form submission: {pdf_path}")
        
        # Try to generate the PDF
        try:
            generate_pdf_from_form(form.title, form_structure, answers, pdf_path)
            current_app.logger.info(f"PDF successfully generated: {pdf_path}")
        except Exception as pdf_error:
            current_app.logger.error(f"PDF generation failed: {str(pdf_error)}")
            raise ValueError(f"Could not generate PDF: {str(pdf_error)}")
        
        # Mark the form as complete
        response.answers = json.dumps(answers)
        response.is_complete = True
        response.pdf_path = pdf_path
        response.submitted_at = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"Form response {response.id} marked as complete")
        
        # Prepare form data for context
        form_data = {
            'form_id': form.id,
            'form_title': form.title,
            'user_id': current_user.id,
            'user_email': current_user.email,
            'user_name': current_user.username,
            'submitted_at': datetime.utcnow().isoformat(),
            'question_count': len(form_structure.get('questions', [])),
            'answered_count': len(answers)
        }
        
        # Send email with PDF to the user
        email_result = send_form_email(
            recipient_email=current_user.email,
            form_title=form.title,
            pdf_path=pdf_path,
            form_data=form_data
        )
        
        # Log the email sending result
        if email_result.get('success'):
            current_app.logger.info(f"Form '{form.title}' submitted successfully and email sent")
            email_sent = True
        else:
            current_app.logger.warning(f"Form '{form.title}' submitted but email could not be sent: {email_result.get('message')}")
            email_sent = False
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Form submitted successfully',
            'email_sent': email_sent,
            'email_details': email_result
        })
        
    except Exception as e:
        current_app.logger.error(f"Form submission error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error submitting form: {str(e)}'}), 500

@form_bp.route('/<int:form_id>/delete', methods=['POST'])
@login_required
def delete_form(form_id):
    """Delete a form and its associated file"""
    if not current_user.is_admin:
        flash('Only administrators can delete forms', 'danger')
        return redirect(url_for('form.form_list'))
    
    form = Form.query.get_or_404(form_id)
    
    try:
        # Delete form file if it exists
        if form.file_path and os.path.exists(form.file_path):
            os.remove(form.file_path)
            current_app.logger.info(f"Deleted form file: {form.file_path}")
        
        # Delete form responses and their associated PDF files
        responses = FormResponse.query.filter_by(form_id=form_id).all()
        for response in responses:
            # Delete PDF if it exists
            if response.pdf_path and os.path.exists(response.pdf_path):
                os.remove(response.pdf_path)
                current_app.logger.info(f"Deleted response PDF: {response.pdf_path}")
            
            # Delete response
            db.session.delete(response)
        
        # Delete form
        db.session.delete(form)
        db.session.commit()
        
        current_app.logger.info(f"Form ID {form_id} deleted successfully")
        
        # Check if this is an AJAX request
        is_ajax_request = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if is_ajax_request:
            return jsonify({
                'success': True,
                'message': f'Form "{form.title}" deleted successfully'
            })
        else:
            flash(f'Form "{form.title}" and all associated responses have been deleted', 'success')
            return redirect(url_for('form.form_list'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting form: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': f'Error deleting form: {str(e)}'
            }), 500
        else:
            flash(f'Error deleting form: {str(e)}', 'danger')
            return redirect(url_for('form.form_list'))
