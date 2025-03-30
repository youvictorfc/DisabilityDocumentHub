import os
import logging
from datetime import datetime
from fpdf import FPDF

def generate_pdf_from_form(form_title, form_structure, answers, output_path):
    """
    Generate a PDF document from a completed form.
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.set_font("Arial", "B", 16)
        
        # Title
        pdf.cell(0, 10, form_title, 0, 1, "C")
        pdf.ln(5)
        
        # Date
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Completed on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "R")
        pdf.ln(5)
        
        # Questions and answers
        pdf.set_font("Arial", "B", 12)
        
        questions = form_structure.get('questions', [])
        for question in questions:
            question_id = question.get('id')
            # Get question text from various possible field names
            question_text = question.get('question_text') or question.get('question') or question.get('label') or f"Question {question_id}"
            # Get field type from possible variations
            field_type = question.get('field_type') or question.get('type') or 'text'
            
            # Question
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 10, question_text)
            
            # Answer
            pdf.set_font("Arial", "", 12)
            
            if question_id in answers:
                answer = answers[question_id]
                
                if field_type in ['checkbox', 'radio', 'select']:
                    # For multiple choice, display the selected option(s)
                    if isinstance(answer, list):
                        for option in answer:
                            pdf.multi_cell(0, 10, f"- {option}")
                    else:
                        pdf.multi_cell(0, 10, f"- {answer}")
                else:
                    # For text fields, display the text
                    pdf.multi_cell(0, 10, str(answer))
            else:
                pdf.multi_cell(0, 10, "No answer provided")
            
            pdf.ln(5)
        
        # Save the PDF
        pdf.output(output_path)
        return True
    
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        raise Exception(f"Failed to generate PDF: {str(e)}")
