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
    # Only show forms that haven't been soft-deleted
    forms = Form.query.filter_by(is_deleted=False).all()
    
    # Get user's in-progress forms
    user_responses = FormResponse.query.filter_by(
        user_id=current_user.id,
        is_complete=False
    ).all()
    
    in_progress_forms = []
    for response in user_responses:
        # Only include responses for non-deleted forms or include all if admin
        if not response.form.is_deleted or current_user.is_admin:
            in_progress_forms.append({
                'form_id': response.form_id,
                'form_title': response.form.title + (" (Deleted)" if response.form.is_deleted else ""),
                'response_id': response.id,
                'updated_at': response.updated_at,
                'is_deleted_form': response.form.is_deleted
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
        
        # Make sure upload directory exists
        os.makedirs(current_app.config['FORM_UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['FORM_UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Enhanced logging for form upload process
        current_app.logger.info("=" * 50)
        current_app.logger.info(f"FORM UPLOAD PROCESS STARTED")
        current_app.logger.info(f"Form Title: {title}")
        current_app.logger.info(f"Filename: {filename}")
        current_app.logger.info(f"File Type: {file_extension}")
        current_app.logger.info(f"File Path: {file_path}")
        current_app.logger.info(f"Uploaded By: {current_user.username} (ID: {current_user.id})")
        current_app.logger.info("=" * 50)
        
        # Variable to hold form structure
        form_structure = None
        questions_count = 0
        
        try:
            # Flag to track if we should use OpenAI extraction
            use_openai_extraction = True
            current_app.logger.info("Starting form type detection to determine extraction method...")
            
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
            
            # Special case for the Act as an Advocate Form
            elif "advocate" in filename.lower() or "act as an advocate" in filename.lower():
                current_app.logger.info("Detected an Act as an Advocate form upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.advocate_form_template import get_advocate_form_template, is_advocate_form
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using advocate form template for .docx file")
                    form_structure = {
                        "questions": get_advocate_form_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using advocate form template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like an advocate form
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_advocate_form(content):
                            current_app.logger.info("Detected advocate form content, using specialized template")
                            form_structure = {
                                "questions": get_advocate_form_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using advocate form template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not an advocate form or couldn't extract content, proceed to normal extraction
                            current_app.logger.info("Content doesn't appear to be an advocate form, proceeding with normal extraction")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is an advocate form: {str(e)}")
                        
            # Special case for the Complaints Form
            elif "complaint" in filename.lower() or "complaints form" in filename.lower():
                current_app.logger.info("Detected a Complaints Form upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.complaints_form_template import get_complaints_form_template, is_complaints_form
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using complaints form template for .docx file")
                    form_structure = {
                        "questions": get_complaints_form_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using complaints form template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like a complaints form
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_complaints_form(content):
                            current_app.logger.info("Detected complaints form content, using specialized template")
                            form_structure = {
                                "questions": get_complaints_form_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using complaints form template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not a complaints form or couldn't extract content, proceed to normal extraction
                            current_app.logger.info("Content doesn't appear to be a complaints form, proceeding with normal extraction")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is a complaints form: {str(e)}")
                        
            # Special case for the Conflict of Interest Form
            elif "conflict" in filename.lower() or "conflict of interest" in filename.lower():
                current_app.logger.info("Detected a Conflict of Interest Form upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.conflict_form_template import get_conflict_form_template, is_conflict_form
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using conflict form template for .docx file")
                    form_structure = {
                        "questions": get_conflict_form_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using conflict form template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like a conflict form
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_conflict_form(content):
                            current_app.logger.info("Detected conflict form content, using specialized template")
                            form_structure = {
                                "questions": get_conflict_form_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using conflict form template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not a conflict form or couldn't extract content, proceed to normal extraction
                            current_app.logger.info("Content doesn't appear to be a conflict form, proceeding with normal extraction")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is a conflict form: {str(e)}")
                        
            # Special case for the Feedback Form
            elif "feedback" in filename.lower() or "feedback form" in filename.lower():
                current_app.logger.info("Detected a Feedback Form upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.feedback_form_template import get_feedback_form_template, is_feedback_form
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using feedback form template for .docx file")
                    form_structure = {
                        "questions": get_feedback_form_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using feedback form template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like a feedback form
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_feedback_form(content):
                            current_app.logger.info("Detected feedback form content, using specialized template")
                            form_structure = {
                                "questions": get_feedback_form_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using feedback form template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not a feedback form or couldn't extract content, proceed to normal extraction
                            current_app.logger.info("Content doesn't appear to be a feedback form, proceeding with normal extraction")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is a feedback form: {str(e)}")
                        
            # Check for Meeting Minutes
            elif "meeting minutes" in filename.lower() or "meeting_minutes" in filename.lower():
                current_app.logger.info("Detected a Meeting Minutes upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.meeting_minutes_template import get_meeting_minutes_template, is_meeting_minutes
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using meeting minutes template for .docx file")
                    form_structure = {
                        "questions": get_meeting_minutes_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using meeting minutes template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like meeting minutes
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_meeting_minutes(content):
                            current_app.logger.info("Detected meeting minutes content, using specialized template")
                            form_structure = {
                                "questions": get_meeting_minutes_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using meeting minutes template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not meeting minutes or couldn't extract content, proceed to check for next form type
                            current_app.logger.info("Content doesn't appear to be meeting minutes, checking for other form types")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is meeting minutes: {str(e)}")
                        
            # Check for Home Safety Checklist
            elif "home safety" in filename.lower() or "home_safety_checklist" in filename.lower():
                current_app.logger.info("Detected a Home Safety Checklist upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.home_safety_checklist_template import get_home_safety_checklist_template, is_home_safety_checklist
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using home safety checklist template for .docx file")
                    form_structure = {
                        "questions": get_home_safety_checklist_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using home safety checklist template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like a home safety checklist
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_home_safety_checklist(content):
                            current_app.logger.info("Detected home safety checklist content, using specialized template")
                            form_structure = {
                                "questions": get_home_safety_checklist_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using home safety checklist template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not a home safety checklist or couldn't extract content, proceed to check for next form type
                            current_app.logger.info("Content doesn't appear to be a home safety checklist, checking for other form types")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is a home safety checklist: {str(e)}")
            
            # Check for Hazardous Substances Checklist
            elif "hazardous substances" in filename.lower() or "hazardous_substances_checklist" in filename.lower():
                current_app.logger.info("Detected a Hazardous Substances Checklist upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.hazardous_substances_checklist_template import get_hazardous_substances_checklist_template, is_hazardous_substances_checklist
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using hazardous substances checklist template for .docx file")
                    form_structure = {
                        "questions": get_hazardous_substances_checklist_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using hazardous substances checklist template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like a hazardous substances checklist
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_hazardous_substances_checklist(content):
                            current_app.logger.info("Detected hazardous substances checklist content, using specialized template")
                            form_structure = {
                                "questions": get_hazardous_substances_checklist_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using hazardous substances checklist template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not a hazardous substances checklist or couldn't extract content, proceed to check for general hazard form
                            current_app.logger.info("Content doesn't appear to be a hazardous substances checklist, checking for general hazard form")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is a hazardous substances checklist: {str(e)}")
            
            # Check for Plant-Asset Hazard Checklist (more specific than general hazard form)
            elif "plant-asset" in filename.lower() or "plant_asset" in filename.lower() or "new plant" in filename.lower():
                current_app.logger.info("Detected a Plant-Asset Hazard Checklist upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.plant_asset_hazard_checklist_template import get_plant_asset_hazard_checklist_template, is_plant_asset_hazard_checklist
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using plant-asset hazard checklist template for .docx file")
                    form_structure = {
                        "questions": get_plant_asset_hazard_checklist_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using plant-asset hazard checklist template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like a plant-asset hazard checklist
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_plant_asset_hazard_checklist(content):
                            current_app.logger.info("Detected plant-asset hazard checklist content, using specialized template")
                            form_structure = {
                                "questions": get_plant_asset_hazard_checklist_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using plant-asset hazard checklist template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not a plant-asset hazard checklist or couldn't extract content, proceed to check for general hazard form
                            current_app.logger.info("Content doesn't appear to be a plant-asset hazard checklist, checking for general hazard form")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is a plant-asset hazard checklist: {str(e)}")
            
            # Check for general Hazard Form
            elif "hazard" in filename.lower() or "hazard form" in filename.lower():
                current_app.logger.info("Detected a Hazard Form upload, using specialized template")
                # Import directly here to avoid circular imports
                from services.form.hazard_form_template import get_hazard_form_template, is_hazard_form
                
                # For docx files, we immediately use the template
                if filename.lower().endswith(".docx"):
                    current_app.logger.info("Using hazard form template for .docx file")
                    form_structure = {
                        "questions": get_hazard_form_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using hazard form template with {questions_count} fields")
                    use_openai_extraction = False
                # For other file types, we try to extract content and check if it looks like a hazard form
                else:
                    try:
                        # Try to extract text content if applicable
                        from services.document.document_service import extract_text_from_file
                        content = extract_text_from_file(file_path)
                        if content and is_hazard_form(content):
                            current_app.logger.info("Detected hazard form content, using specialized template")
                            form_structure = {
                                "questions": get_hazard_form_template()
                            }
                            questions_count = len(form_structure.get('questions', []))
                            current_app.logger.info(f"Using hazard form template with {questions_count} fields")
                            use_openai_extraction = False
                        else:
                            # Not a hazard form or couldn't extract content, proceed to normal extraction
                            current_app.logger.info("Content doesn't appear to be a hazard form, proceeding with normal extraction")
                    except Exception as e:
                        current_app.logger.info(f"Error checking if file is a hazard form: {str(e)}")
            
            # Use OpenAI extraction if we haven't already used a template
            if use_openai_extraction:
                # Extract form structure using OpenAI - preserve EXACT questions and order
                current_app.logger.info("=" * 50)
                current_app.logger.info(f"NO TEMPLATE MATCH FOUND - USING AI-BASED EXTRACTION")
                current_app.logger.info(f"Extracting EXACT form structure from {file_path} using enhanced OpenAI processing")
                current_app.logger.info("Using multi-pass verification with JSON schema to ensure accuracy")
                current_app.logger.info("=" * 50)
                
                try:
                    # Extract the form structure
                    form_structure = extract_form_structure(file_path)
                    
                    # Log the extracted structure for debugging
                    current_app.logger.debug(f"Extracted form structure: {json.dumps(form_structure)[:500]}...")
                    
                    # Validate the extracted structure
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Successfully extracted {questions_count} questions in their exact original form")
                    
                    # Log the first few questions to provide insight into extraction quality
                    if questions_count > 0:
                        current_app.logger.info("Sample of extracted questions:")
                        for i, question in enumerate(form_structure.get('questions', [])[:3]):  # Show first 3 questions
                            current_app.logger.info(f"  Q{i+1}: {question.get('question_text', '')[:100]}{'...' if len(question.get('question_text', '')) > 100 else ''}")
                        if questions_count > 3:
                            current_app.logger.info(f"  ...and {questions_count - 3} more questions")
                    
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
                created_at=datetime.utcnow(),
                user_id=current_user.id  # Track which admin uploaded the form
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

@form_bp.route('/<int:form_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    """Allow administrators to edit a form's title, description, and optionally replace the document"""
    if not current_user.is_admin:
        flash('Only administrators can edit forms', 'danger')
        return redirect(url_for('form.form_list'))
    
    form = Form.query.get_or_404(form_id)
    
    if form.is_deleted:
        flash('Cannot edit a deleted form', 'danger')
        return redirect(url_for('form.form_list'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        file = request.files.get('form_file')
        
        if not title:
            flash('Form title is required', 'danger')
            return render_template('forms/form_edit.html', form=form)
        
        # Update basic form information
        form.title = title
        form.description = description
        
        # Only process file if a new one was uploaded
        if file and file.filename:
            # Check file extension
            supported_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'txt', 'doc', 'docx'}
            file_extension = ''
            
            if '.' in file.filename:
                file_extension = file.filename.rsplit('.', 1)[1].lower()
            
            if not file_extension or file_extension not in supported_extensions:
                flash(f'File type "{file_extension}" not supported. Please use PDF, JPG, PNG, GIF, or TXT formats.', 'danger')
                return render_template('forms/form_edit.html', form=form)
                
            # Check file size - OpenAI has limits (typically ~20-25MB)
            max_size_mb = 20
            if file.content_length and file.content_length > max_size_mb * 1024 * 1024:
                file_size_mb = file.content_length / (1024 * 1024)
                flash(f'File too large ({file_size_mb:.1f} MB). Maximum size is {max_size_mb} MB.', 'danger')
                return render_template('forms/form_edit.html', form=form)
            
            # Delete the old file if it exists
            if form.file_path and os.path.exists(form.file_path):
                try:
                    os.remove(form.file_path)
                    current_app.logger.info(f"Deleted old form file: {form.file_path}")
                except Exception as e:
                    current_app.logger.error(f"Error deleting old form file: {str(e)}")
            
            # Save the new file
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['FORM_UPLOAD_FOLDER'], filename)
            file.save(file_path)
            form.file_path = file_path
            
            # Make sure upload directory exists
            os.makedirs(current_app.config['FORM_UPLOAD_FOLDER'], exist_ok=True)
            
            try:
                # Extract form structure using OpenAI - preserve EXACT questions and order
                current_app.logger.info(f"Re-extracting form structure from new file: {file_path}")
                
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
                            
                # Special case for the Act as an Advocate Form
                elif "advocate" in filename.lower() or "act as an advocate" in filename.lower():
                    current_app.logger.info("Detected an Act as an Advocate form upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.advocate_form_template import get_advocate_form_template, is_advocate_form
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using advocate form template for .docx file")
                        form_structure = {
                            "questions": get_advocate_form_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using advocate form template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like an advocate form
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_advocate_form(content):
                                current_app.logger.info("Detected advocate form content, using specialized template")
                                form_structure = {
                                    "questions": get_advocate_form_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using advocate form template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not an advocate form or couldn't extract content, proceed to normal extraction
                                current_app.logger.info("Content doesn't appear to be an advocate form, proceeding with normal extraction")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is an advocate form: {str(e)}")
                            
                # Special case for the Complaints Form
                elif "complaint" in filename.lower() or "complaints form" in filename.lower():
                    current_app.logger.info("Detected a Complaints Form upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.complaints_form_template import get_complaints_form_template, is_complaints_form
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using complaints form template for .docx file")
                        form_structure = {
                            "questions": get_complaints_form_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using complaints form template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a complaints form
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_complaints_form(content):
                                current_app.logger.info("Detected complaints form content, using specialized template")
                                form_structure = {
                                    "questions": get_complaints_form_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using complaints form template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a complaints form or couldn't extract content, proceed to normal extraction
                                current_app.logger.info("Content doesn't appear to be a complaints form, proceeding with normal extraction")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a complaints form: {str(e)}")
                            
                # Special case for the Conflict of Interest Form
                elif "conflict" in filename.lower() or "conflict of interest" in filename.lower():
                    current_app.logger.info("Detected a Conflict of Interest Form upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.conflict_form_template import get_conflict_form_template, is_conflict_form
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using conflict form template for .docx file")
                        form_structure = {
                            "questions": get_conflict_form_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using conflict form template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a conflict form
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_conflict_form(content):
                                current_app.logger.info("Detected conflict form content, using specialized template")
                                form_structure = {
                                    "questions": get_conflict_form_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using conflict form template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a conflict form or couldn't extract content, proceed to normal extraction
                                current_app.logger.info("Content doesn't appear to be a conflict form, proceeding with normal extraction")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a conflict form: {str(e)}")
                            
                # Special case for Meeting Minutes
                elif "meeting minutes" in filename.lower() or "meeting_minutes" in filename.lower():
                    current_app.logger.info("Detected a Meeting Minutes upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.meeting_minutes_template import get_meeting_minutes_template, is_meeting_minutes
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using meeting minutes template for .docx file")
                        form_structure = {
                            "questions": get_meeting_minutes_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using meeting minutes template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like meeting minutes
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_meeting_minutes(content):
                                current_app.logger.info("Detected meeting minutes content, using specialized template")
                                form_structure = {
                                    "questions": get_meeting_minutes_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using meeting minutes template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not meeting minutes or couldn't extract content, proceed to check for next form type
                                current_app.logger.info("Content doesn't appear to be meeting minutes, checking for other form types")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is meeting minutes: {str(e)}")
                            
                # Special case for Home Safety Checklist
                elif "home safety" in filename.lower() or "home_safety_checklist" in filename.lower():
                    current_app.logger.info("Detected a Home Safety Checklist upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.home_safety_checklist_template import get_home_safety_checklist_template, is_home_safety_checklist
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using home safety checklist template for .docx file")
                        form_structure = {
                            "questions": get_home_safety_checklist_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using home safety checklist template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a home safety checklist
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_home_safety_checklist(content):
                                current_app.logger.info("Detected home safety checklist content, using specialized template")
                                form_structure = {
                                    "questions": get_home_safety_checklist_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using home safety checklist template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a home safety checklist or couldn't extract content, proceed to normal extraction
                                current_app.logger.info("Content doesn't appear to be a home safety checklist, proceeding with normal extraction")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a home safety checklist: {str(e)}")
                
                # Special case for the Hazard Form
                # Check for Hazardous Substances Checklist first (more specific than general hazard form)
                elif "hazardous substances" in filename.lower() or "hazardous_substances_checklist" in filename.lower():
                    current_app.logger.info("Detected a Hazardous Substances Checklist upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.hazardous_substances_checklist_template import get_hazardous_substances_checklist_template, is_hazardous_substances_checklist
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using hazardous substances checklist template for .docx file")
                        form_structure = {
                            "questions": get_hazardous_substances_checklist_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using hazardous substances checklist template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a hazardous substances checklist
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_hazardous_substances_checklist(content):
                                current_app.logger.info("Detected hazardous substances checklist content, using specialized template")
                                form_structure = {
                                    "questions": get_hazardous_substances_checklist_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using hazardous substances checklist template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a hazardous substances checklist or couldn't extract content, proceed to check for general hazard form
                                current_app.logger.info("Content doesn't appear to be a hazardous substances checklist, checking for general hazard form")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a hazardous substances checklist: {str(e)}")
                
                # Check for Plant-Asset Hazard Checklist (more specific than general hazard form)
                elif "plant-asset" in filename.lower() or "plant_asset" in filename.lower() or "new plant" in filename.lower():
                    current_app.logger.info("Detected a Plant-Asset Hazard Checklist upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.plant_asset_hazard_checklist_template import get_plant_asset_hazard_checklist_template, is_plant_asset_hazard_checklist
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using plant-asset hazard checklist template for .docx file")
                        form_structure = {
                            "questions": get_plant_asset_hazard_checklist_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using plant-asset hazard checklist template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a plant-asset hazard checklist
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_plant_asset_hazard_checklist(content):
                                current_app.logger.info("Detected plant-asset hazard checklist content, using specialized template")
                                form_structure = {
                                    "questions": get_plant_asset_hazard_checklist_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using plant-asset hazard checklist template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a plant-asset hazard checklist or couldn't extract content, proceed to check for general hazard form
                                current_app.logger.info("Content doesn't appear to be a plant-asset hazard checklist, checking for general hazard form")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a plant-asset hazard checklist: {str(e)}")
                
                # Check for general Hazard Form
                elif "hazard" in filename.lower() or "hazard form" in filename.lower():
                    current_app.logger.info("Detected a Hazard Form upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.hazard_form_template import get_hazard_form_template, is_hazard_form
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using hazard form template for .docx file")
                        form_structure = {
                            "questions": get_hazard_form_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using hazard form template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a hazard form
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_hazard_form(content):
                                current_app.logger.info("Detected hazard form content, using specialized template")
                                form_structure = {
                                    "questions": get_hazard_form_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using hazard form template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a hazard form or couldn't extract content, proceed to normal extraction
                                current_app.logger.info("Content doesn't appear to be a hazard form, proceeding with normal extraction")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a hazard form: {str(e)}")
                            
                # Special case for the Feedback Form
                elif "feedback" in filename.lower() or "feedback form" in filename.lower():
                    current_app.logger.info("Detected a Feedback Form upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.feedback_form_template import get_feedback_form_template, is_feedback_form
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using feedback form template for .docx file")
                        form_structure = {
                            "questions": get_feedback_form_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using feedback form template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a feedback form
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_feedback_form(content):
                                current_app.logger.info("Detected feedback form content, using specialized template")
                                form_structure = {
                                    "questions": get_feedback_form_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using feedback form template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a feedback form or couldn't extract content, proceed to normal extraction
                                current_app.logger.info("Content doesn't appear to be a feedback form, proceeding with normal extraction")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a feedback form: {str(e)}")
                
                # Special case for the Root Cause Analysis Form - Always use template regardless of file format
                elif "root cause" in filename.lower() or "analysis" in filename.lower() or "rca" in filename.lower():
                    current_app.logger.info("==== DETECTED ROOT CAUSE ANALYSIS FORM - USING SPECIALIZED TEMPLATE ====")
                    # Import directly here to avoid circular imports
                    from services.form.root_cause_analysis_template import get_root_cause_analysis_template
                    
                    # Always use the template for any file containing root cause analysis keywords in the name
                    # This provides consistent form field extraction regardless of file format
                    current_app.logger.info("Using root cause analysis template for ALL file formats with matching filename")
                    form_structure = {
                        "questions": get_root_cause_analysis_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using root cause analysis template with {questions_count} fields")
                    
                    # Print sample of fields for verification
                    current_app.logger.info("Sample fields from Root Cause Analysis template:")
                    for i, q in enumerate(form_structure.get('questions', [])[:5]):
                        current_app.logger.info(f"  Field {i+1}: {q.get('question_text', '')[:100]}...")
                    
                    use_openai_extraction = False
                    current_app.logger.info("==== ROOT CAUSE ANALYSIS TEMPLATE APPLIED SUCCESSFULLY ====")
                    current_app.logger.info(f"Original filename: {filename}")
                    current_app.logger.info(f"File path: {file_path}")
                
                # Check for Vehicle Safety Check Sheet
                if "vehicle" in filename.lower() or "safety check" in filename.lower() or "vehicle safety" in filename.lower():
                    current_app.logger.info("Detected a Vehicle Safety Check Sheet upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.vehicle_safety_check_template import get_vehicle_safety_check_template, is_vehicle_safety_check
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using vehicle safety check template for .docx file")
                        form_structure = {
                            "questions": get_vehicle_safety_check_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using vehicle safety check template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a vehicle safety check
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_vehicle_safety_check(content):
                                current_app.logger.info("Detected vehicle safety check content, using specialized template")
                                form_structure = {
                                    "questions": get_vehicle_safety_check_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using vehicle safety check template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a vehicle safety check or couldn't extract content, proceed to normal extraction
                                current_app.logger.info("Content doesn't appear to be a vehicle safety check, proceeding with normal extraction")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a vehicle safety check: {str(e)}")
                
                # Check for Waste Risk Assessment Checklist
                elif "waste" in filename.lower() or "risk assessment" in filename.lower() or "waste risk" in filename.lower():
                    current_app.logger.info("Detected a Waste Risk Assessment Checklist upload, using specialized template")
                    # Import directly here to avoid circular imports
                    from services.form.waste_risk_assessment_template import get_waste_risk_assessment_template, is_waste_risk_assessment
                    
                    # For docx files, we immediately use the template
                    if filename.lower().endswith(".docx"):
                        current_app.logger.info("Using waste risk assessment template for .docx file")
                        form_structure = {
                            "questions": get_waste_risk_assessment_template()
                        }
                        questions_count = len(form_structure.get('questions', []))
                        current_app.logger.info(f"Using waste risk assessment template with {questions_count} fields")
                        use_openai_extraction = False
                    # For other file types, we try to extract content and check if it looks like a waste risk assessment
                    else:
                        try:
                            # Try to extract text content if applicable
                            from services.document.document_service import extract_text_from_file
                            content = extract_text_from_file(file_path)
                            if content and is_waste_risk_assessment(content):
                                current_app.logger.info("Detected waste risk assessment content, using specialized template")
                                form_structure = {
                                    "questions": get_waste_risk_assessment_template()
                                }
                                questions_count = len(form_structure.get('questions', []))
                                current_app.logger.info(f"Using waste risk assessment template with {questions_count} fields")
                                use_openai_extraction = False
                            else:
                                # Not a waste risk assessment or couldn't extract content, proceed to normal extraction
                                current_app.logger.info("Content doesn't appear to be a waste risk assessment, proceeding with normal extraction")
                        except Exception as e:
                            current_app.logger.info(f"Error checking if file is a waste risk assessment: {str(e)}")
                
                # Check for Nutrition Assessment form FIRST (more specific matching than generic "nutrition")
                elif "nutrition assessment" in filename.lower() or "nutritional assessment" in filename.lower():
                    current_app.logger.info("==== DETECTED NUTRITION ASSESSMENT FORM - USING SPECIALIZED TEMPLATE ====")
                    # Import directly here to avoid circular imports
                    from services.form.nutrition_assessment_template import get_nutrition_assessment_template
                    
                    # Always use the template for Nutrition Assessment form regardless of file format
                    current_app.logger.info("Using Nutrition Assessment template for ALL file formats with matching filename")
                    form_structure = {
                        "questions": get_nutrition_assessment_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using Nutrition Assessment template with {questions_count} fields")
                    
                    # Print sample of fields for verification
                    current_app.logger.info("Sample fields from Nutrition Assessment template:")
                    for i, q in enumerate(form_structure.get('questions', [])[:5]):
                        current_app.logger.info(f"  Field {i+1}: {q.get('question_text', '')[:100]}...")
                    
                    use_openai_extraction = False
                    current_app.logger.info("==== NUTRITION ASSESSMENT TEMPLATE APPLIED SUCCESSFULLY ====")
                    current_app.logger.info(f"Original filename: {filename}")
                    current_app.logger.info(f"File path: {file_path}")
                
                # Check for Nutrition and Swallowing Risk Checklist - Always use template regardless of file format
                elif "nutrition and swallowing" in filename.lower() or "swallowing risk" in filename.lower() or "nutrition checklist" in filename.lower():
                    current_app.logger.info("==== DETECTED NUTRITION AND SWALLOWING RISK CHECKLIST - USING SPECIALIZED TEMPLATE ====")
                    # Import directly here to avoid circular imports
                    from services.form.nutrition_swallowing_risk_template import get_nutrition_swallowing_risk_template
                    
                    # Always use the template for any file containing nutrition and swallowing keywords in the name
                    # This provides consistent form field extraction regardless of file format
                    current_app.logger.info("Using nutrition and swallowing risk template for ALL file formats with matching filename")
                    form_structure = {
                        "questions": get_nutrition_swallowing_risk_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using nutrition and swallowing risk template with {questions_count} fields")
                    
                    # Print sample of fields for verification
                    current_app.logger.info("Sample fields from Nutrition and Swallowing Risk template:")
                    for i, q in enumerate(form_structure.get('questions', [])[:5]):
                        current_app.logger.info(f"  Field {i+1}: {q.get('question_text', '')[:100]}...")
                    
                    use_openai_extraction = False
                    current_app.logger.info("==== NUTRITION AND SWALLOWING RISK TEMPLATE APPLIED SUCCESSFULLY ====")
                    current_app.logger.info(f"Original filename: {filename}")
                    current_app.logger.info(f"File path: {file_path}")
                
                # Special direct match for Mealtime Food Safety Audit Checklist
                elif "Mealtime Food Safety Audit Checklist" in file_path:
                    current_app.logger.info("===== EXACT MATCH FOR Mealtime Food Safety Audit Checklist =====")
                    # Always use the specialized template for this exact file
                    from services.form.mealtime_safety_audit_template import get_mealtime_safety_audit_template
                    
                    current_app.logger.info("========== USING MEALTIME FOOD SAFETY AUDIT TEMPLATE ==========")
                    form_structure = {
                        "questions": get_mealtime_safety_audit_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using mealtime food safety audit template with {questions_count} fields")
                    current_app.logger.info(f"File path: {file_path}")
                    current_app.logger.info(f"Filename: {filename}")
                    
                    # Print out the first few fields to confirm template is working
                    for i, q in enumerate(form_structure.get('questions', [])[:3]):
                        current_app.logger.info(f"Sample field {i+1}: {q.get('question_text', '')[:50]}")
                    
                    use_openai_extraction = False
                
                # More general match for Mealtime Food Safety Audit Checklist
                elif "mealtime" in filename.lower() or "food safety" in filename.lower() or "audit checklist" in filename.lower():
                    current_app.logger.info("Detected a Mealtime Food Safety Audit Checklist upload, using specialized template")
                    # Always use the specialized template for mealtime food safety audit forms, regardless of file type
                    from services.form.mealtime_safety_audit_template import get_mealtime_safety_audit_template
                    
                    current_app.logger.info("========== USING MEALTIME FOOD SAFETY AUDIT TEMPLATE ==========")
                    form_structure = {
                        "questions": get_mealtime_safety_audit_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using mealtime food safety audit template with {questions_count} fields")
                    
                    # Print out the first few fields to confirm template is working
                    for i, q in enumerate(form_structure.get('questions', [])[:3]):
                        current_app.logger.info(f"Sample field {i+1}: {q.get('question_text', '')[:50]}")
                    
                    use_openai_extraction = False
                
                # Check for Food Diary Form - more specific pattern matching for reliable detection
                elif "food diary" in filename.lower() or (("food" in filename.lower() or "meal" in filename.lower()) and ("diary" in filename.lower() or "log" in filename.lower())):
                    current_app.logger.info("Detected a Food Diary Form upload, using specialized template")
                    # Always use the specialized template for food diary forms, regardless of file type
                    from services.form.food_diary_template import get_food_diary_template
                    
                    current_app.logger.info("========== USING FOOD DIARY TEMPLATE ==========")
                    form_structure = {
                        "questions": get_food_diary_template()
                    }
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Using food diary template with {questions_count} fields")
                    
                    # Print out the first few fields to confirm template is working
                    for i, q in enumerate(form_structure.get('questions', [])[:3]):
                        current_app.logger.info(f"Sample field {i+1}: {q.get('question_text', '')[:50]}")
                    
                    use_openai_extraction = False

                # No duplicate section needed - Root Cause Analysis Form is already handled earlier in the code
                
                # Use OpenAI extraction if we haven't already used a template
                if use_openai_extraction:
                    # Extract form structure using OpenAI - preserve EXACT questions and order
                    current_app.logger.info("=" * 50)
                    current_app.logger.info(f"NO TEMPLATE MATCH FOUND - USING AI-BASED EXTRACTION FOR EDITED FORM")
                    current_app.logger.info(f"Extracting EXACT form structure from {file_path} using enhanced OpenAI processing")
                    current_app.logger.info("Using multi-pass verification with JSON schema to ensure accuracy")
                    current_app.logger.info("=" * 50)
                    
                    # Extract the form structure
                    form_structure = extract_form_structure(file_path)
                    
                    # Log the extracted structure for debugging
                    current_app.logger.debug(f"Extracted form structure: {json.dumps(form_structure)[:500]}...")
                    
                    # Validate the extracted structure
                    questions_count = len(form_structure.get('questions', []))
                    current_app.logger.info(f"Successfully extracted {questions_count} questions in their exact original form")
                    
                    # Log the first few questions to provide insight into extraction quality
                    if questions_count > 0:
                        current_app.logger.info("Sample of extracted questions:")
                        for i, question in enumerate(form_structure.get('questions', [])[:3]):  # Show first 3 questions
                            current_app.logger.info(f"  Q{i+1}: {question.get('question_text', '')[:100]}{'...' if len(question.get('question_text', '')) > 100 else ''}")
                        if questions_count > 3:
                            current_app.logger.info(f"  ...and {questions_count - 3} more questions")
                    
                    # Check if we have a reasonable number of questions
                    if questions_count == 0:
                        raise ValueError("No questions could be extracted from the form document. Please try a different file or format.")
                
                # Update form structure in the database
                form.structure = json.dumps(form_structure)
                questions_count = len(form_structure.get('questions', []))
                flash(f'Form updated with new document. {questions_count} questions extracted.', 'success')
                
            except Exception as extraction_error:
                current_app.logger.error(f"Form extraction error during edit: {str(extraction_error)}")
                flash(f'Error extracting form fields from new document: {str(extraction_error)}', 'danger')
                
                # Clean up the file
                if os.path.exists(file_path):
                    os.remove(file_path)
                return render_template('forms/form_edit.html', form=form)
        else:
            # If no new file was uploaded, just update the basic info
            flash('Form information updated successfully.', 'success')
        
        # Save the changes
        try:
            db.session.commit()
            return redirect(url_for('form.form_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating form: {str(e)}")
            flash(f'Error updating form: {str(e)}', 'danger')
            return render_template('forms/form_edit.html', form=form)
    
    # GET request - show the edit form
    return render_template('forms/form_edit.html', form=form)

@form_bp.route('/<int:form_id>/fill', methods=['GET'])
@login_required
def fill_form(form_id):
    form = Form.query.get_or_404(form_id)
    
    # Check if the form has been soft-deleted
    if form.is_deleted and not current_user.is_admin:
        flash('This form is no longer available.', 'danger')
        return redirect(url_for('form.form_list'))
    
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
    
    # Check if the form has been deleted
    form = Form.query.get(response.form_id)
    if form.is_deleted and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'This form is no longer available for editing.'}), 403
    
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
    
    # Check if the form has been soft-deleted and user is not an admin
    if form.is_deleted and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'This form is no longer available for submission.'}), 403
        
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
        
        # Send email with PDF to the user and Minto Disability Services
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
            'message': 'Form submitted successfully and sent to Minto Disability Services',
            'email_sent': email_sent,
            'email_details': email_result
        })
        
    except Exception as e:
        current_app.logger.error(f"Form submission error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error submitting form: {str(e)}'}), 500

@form_bp.route('/<int:form_id>/delete', methods=['POST'])
@login_required
def delete_form(form_id):
    """Soft delete a form while preserving its associated responses"""
    if not current_user.is_admin:
        flash('Only administrators can delete forms', 'danger')
        return redirect(url_for('form.form_list'))
    
    form = Form.query.get_or_404(form_id)
    
    try:
        form_title = form.title  # Store the title before modification
        
        # Only delete the form file if it exists
        if form.file_path and os.path.exists(form.file_path):
            os.remove(form.file_path)
            current_app.logger.info(f"Deleted form file: {form.file_path}")
            form.file_path = None  # Clear the file path reference
        
        # Mark the form as deleted instead of actually deleting it
        form.is_deleted = True
        form.deleted_at = datetime.utcnow()
        db.session.commit()
        
        # Return JSON if AJAX request, otherwise redirect
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': f'Form "{form_title}" deleted successfully.'
            })
        else:
            flash(f'Form "{form_title}" deleted successfully.', 'success')
            return redirect(url_for('form.form_list'))
    
    except Exception as e:
        current_app.logger.error(f"Error deleting form: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
        else:
            flash(f'Error deleting form: {str(e)}', 'danger')
            return redirect(url_for('form.form_list'))

@form_bp.route('/response/<int:response_id>/delete', methods=['POST'])
@login_required
def delete_form_response(response_id):
    """Delete an in-progress form response"""
    form_response = FormResponse.query.get_or_404(response_id)
    
    # Ensure the user owns this response or is an admin
    if form_response.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this form response', 'danger')
        return redirect(url_for('form.form_list'))
    
    try:
        form_title = form_response.form.title  # Store related form title for messaging
        
        # If there's a generated PDF, delete it
        if form_response.pdf_path and os.path.exists(form_response.pdf_path):
            os.remove(form_response.pdf_path)
            current_app.logger.info(f"Deleted form response PDF: {form_response.pdf_path}")
        
        # Actually delete the response
        db.session.delete(form_response)
        db.session.commit()
        
        # Return JSON if AJAX request, otherwise redirect
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': f'Form response for "{form_title}" deleted successfully.'
            })
        else:
            flash(f'Form response for "{form_title}" deleted successfully.', 'success')
            return redirect(url_for('form.form_list'))
    
    except Exception as e:
        current_app.logger.error(f"Error deleting form response: {str(e)}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
        else:
            flash(f'Error deleting form response: {str(e)}', 'danger')
            return redirect(url_for('form.form_list'))