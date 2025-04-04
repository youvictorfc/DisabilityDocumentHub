"""
Template-based fallback solution for the Food Diary Form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any
import re
import os
import docx

def get_food_diary_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Food Diary Form
    with the exact structure matching the document.
    """
    template = []
    
    # Date field
    template.append({
        "id": "q_date",
        "question_text": "Date:",
        "field_type": "date",
        "required": True
    })
    
    # Participant details section
    template.append({
        "id": "q_name",
        "question_text": "Participant Details: Name:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "q_dob",
        "question_text": "DOB:",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "q_gender",
        "question_text": "Gender:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "q_address",
        "question_text": "Address:",
        "field_type": "textarea",
        "required": True
    })
    
    template.append({
        "id": "q_state",
        "question_text": "State:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "q_email",
        "question_text": "Email Address:",
        "field_type": "email",
        "required": True
    })
    
    template.append({
        "id": "q_phone",
        "question_text": "Phone:",
        "field_type": "tel",
        "required": True
    })
    
    template.append({
        "id": "q_contact_person",
        "question_text": "Preferred Contact Person:",
        "field_type": "text",
        "required": True
    })
    
    # Dependency level
    template.append({
        "id": "q_dependency",
        "question_text": "Degree of dependency to provider",
        "field_type": "radio",
        "options": [
            "Low-Generally independent", 
            "Med-Requires some assistance or supervision", 
            "High-Requires constant supervision"
        ],
        "required": True
    })
    
    # Note about dependency evaluation
    template.append({
        "id": "q_dependency_note",
        "question_text": "Note: The degree of dependency has to be evaluated by a qualified person and in consultation with the participants or their rep.",
        "field_type": "info",
        "required": False
    })
    
    # Emergency response procedure
    template.append({
        "id": "q_emergency_procedure",
        "question_text": "Emergency response procedure:",
        "field_type": "textarea",
        "required": True
    })
    
    # Food diary table
    template.append({
        "id": "q_food_diary",
        "question_text": "Food Diary Entries",
        "field_type": "table",
        "columns": ["Type of Meal (Breakfast, Lunch, dinner)", "Type Food and Drinks", "IDDSI Level", "Amount consumed", "Date/Time", "Assisted by"],
        "rows": 20,
        "required": False
    })
    
    return template


def is_food_diary(file_path_or_content: str) -> bool:
    """
    Determine if the file is likely a Food Diary form.
    
    Args:
        file_path_or_content: The path to the file or the content as a string
        
    Returns:
        bool: True if the file appears to be a food diary form
    """
    try:
        content = ""
        
        # Check if the input is a file path
        if os.path.exists(file_path_or_content):
            # Extract text based on file type
            if file_path_or_content.lower().endswith('.docx'):
                doc = docx.Document(file_path_or_content)
                content = '\n'.join([para.text for para in doc.paragraphs])
            else:
                # Assume it's a text file or already content
                with open(file_path_or_content, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
        else:
            # Assume it's already content
            content = file_path_or_content
            
        # Define keywords and patterns that indicate this is a food diary form
        keywords = [
            r"food\s+diary",
            r"type\s+of\s+meal",
            r"breakfast\s*,\s*lunch\s*,\s*dinner",
            r"amount\s+consumed",
            r"iddsi\s+level",
            r"assisted\s+by",
            r"degree\s+of\s+dependency"
        ]
        
        # Create a scoring system - if enough keywords are found, consider it a match
        score = 0
        for keyword in keywords:
            if re.search(keyword, content.lower()):
                score += 1
                
        # If more than 2 keywords match, consider it a food diary form
        return score >= 2
        
    except Exception:
        # If there's any error in processing, default to False
        return False