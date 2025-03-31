import os
import logging
from datetime import datetime
from fpdf import FPDF
from flask import current_app

class FormPDF(FPDF):
    """Extended FPDF class with header and footer for form documents."""
    
    def __init__(self, form_title="Form Submission", organization="Minto Disability Services"):
        super().__init__()
        self.form_title = form_title
        self.organization = organization
        self.set_margins(15, 20, 15)  # Left, top, right margins
        self.set_auto_page_break(True, margin=25)
        
    def header(self):
        # Logo or branding
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, self.organization, 0, 1, 'L')
        
        # Title
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, self.form_title, 0, 1, 'C')
        
        # Date and time
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'R')
        
        # Line break
        self.ln(5)
        
        # Draw a line
        self.line(15, self.get_y(), self.w - 15, self.get_y())
        self.ln(10)
        
    def footer(self):
        # Position cursor at 1.5 cm from bottom
        self.set_y(-15)
        
        # Footer text in gray
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        # Organization info
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, self.organization, 0, 0, 'R')

def sanitize_text_for_pdf(text):
    """Sanitize text to ensure it can be properly displayed in the PDF."""
    if not text:
        return ""
        
    # Convert to string if it's not already
    if not isinstance(text, str):
        text = str(text)
        
    # Replace problematic characters for FPDF
    text = text.replace('\n', ' ')
    text = text.replace('\r', ' ')
    
    # Convert other potentially problematic characters
    char_map = {
        '–': '-',  # en dash
        '—': '-',  # em dash
        ''': "'",  # curly single quote
        ''': "'",  # curly single quote
        '"': '"',  # curly double quote
        '"': '"',  # curly double quote
        '…': '...',  # ellipsis
        '•': '*',  # bullet
    }
    
    for char, replacement in char_map.items():
        text = text.replace(char, replacement)
    
    return text

def generate_pdf_from_form(form_title, form_structure, answers, output_path):
    """
    Generate a PDF document from a completed form.
    
    Args:
        form_title (str): The title of the form
        form_structure (dict): The structure of the form with questions
        answers (dict): The answers to the form questions
        output_path (str): Where to save the PDF file
    
    Returns:
        bool: True if PDF was generated successfully
    """
    try:
        current_app.logger.info(f"Generating PDF for form: {form_title}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Initialize PDF with form title
        pdf = FormPDF(form_title=form_title)
        pdf.add_page()
        
        # Add form metadata section
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Form Information", 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Form Title: {form_title}", 0, 1, 'L')
        pdf.cell(0, 6, f"Submission Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'L')
        pdf.ln(5)
        
        # Add questions and answers
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, "Form Responses", 0, 1, 'L')
        pdf.ln(2)
        
        # Process each question and answer
        questions = form_structure.get('questions', [])
        
        # Get the longest question text for proper formatting
        max_question_length = max([len(q.get('question_text', '')) for q in questions] + [0])
        
        # Create a table-like structure for questions and answers
        table_width = pdf.w - 30  # Total width minus margins
        question_width = min(table_width * 0.4, max_question_length * 2)
        answer_width = table_width - question_width
        
        # Add each question and answer
        for i, question in enumerate(questions):
            # Get question details
            question_id = question.get('id', f'q_{i+1}')
            question_text = question.get('question_text', '')
            if not question_text:
                question_text = question.get('question', '') or question.get('label', '') or f"Question {i+1}"
            
            field_type = question.get('field_type', '') or question.get('type', 'text')
            
            # Draw alternating background for better readability
            if i % 2 == 0:
                pdf.set_fill_color(240, 240, 240)  # Light gray
            else:
                pdf.set_fill_color(255, 255, 255)  # White
            
            # Add question
            current_y = pdf.get_y()
            pdf.set_font('Arial', 'B', 10)
            pdf.multi_cell(table_width, 8, sanitize_text_for_pdf(question_text), 0, 'L', True)
            
            # Add spacing
            pdf.ln(2)
            
            # Add answer
            pdf.set_font('Arial', '', 10)
            
            if question_id in answers:
                answer = answers[question_id]
                
                if field_type in ['checkbox', 'radio', 'select']:
                    # For multiple choice, display the selected option(s)
                    if isinstance(answer, list):
                        for option in answer:
                            pdf.cell(10, 6, "•", 0, 0, 'L')
                            pdf.multi_cell(table_width - 10, 6, sanitize_text_for_pdf(option), 0, 'L')
                    else:
                        answer_text = sanitize_text_for_pdf(answer)
                        pdf.multi_cell(table_width, 6, answer_text, 0, 'L')
                else:
                    # For text fields, display the text
                    answer_text = sanitize_text_for_pdf(answer)
                    pdf.multi_cell(table_width, 6, answer_text, 0, 'L')
            else:
                pdf.set_text_color(150, 150, 150)  # Gray text for no answer
                pdf.multi_cell(table_width, 6, "No answer provided", 0, 'L')
                pdf.set_text_color(0, 0, 0)  # Reset to black
            
            # Add spacing between questions
            pdf.ln(5)
            
            # Add a horizontal line between questions
            pdf.line(15, pdf.get_y(), pdf.w - 15, pdf.get_y())
            pdf.ln(5)
        
        # Add legal disclaimer at the end
        pdf.ln(10)
        pdf.set_font('Arial', 'I', 8)
        pdf.set_text_color(100, 100, 100)  # Dark gray
        disclaimer = "This document contains confidential information and is intended only for authorized recipients. " \
                    "If you have received this document in error, please notify Minto Disability Services immediately."
        pdf.multi_cell(0, 5, disclaimer, 0, 'L')
        
        # Save the PDF
        current_app.logger.info(f"Saving PDF to: {output_path}")
        pdf.output(output_path)
        return True
    
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        raise Exception(f"Failed to generate PDF: {str(e)}")
