"""
Template-based fallback solution for the Medication Administration Form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any
import re
import os

def get_medication_administration_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Medication Administration Form
    with the exact structure matching the document.
    """
    template = []
    
    # Participant details
    template.append({
        "id": "participant_name",
        "question_text": "Participant Name",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "date_of_birth",
        "question_text": "Date of Birth",
        "field_type": "date",
        "required": True
    })
    
    # Staff information section
    template.append({
        "id": "staff_info_header",
        "question_text": "Staff information",
        "field_type": "header",
        "required": False
    })
    
    template.append({
        "id": "support_worker1",
        "question_text": "Support Worker Name/Initial",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "staff_signature1",
        "question_text": "Staff signature",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "date1",
        "question_text": "Date",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "support_worker2",
        "question_text": "Support Worker Name/Initial",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "staff_signature2",
        "question_text": "Staff signature",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "date2",
        "question_text": "Date",
        "field_type": "date",
        "required": False
    })
    
    template.append({
        "id": "support_worker3",
        "question_text": "Support Worker Name/Initial",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "staff_signature3",
        "question_text": "Staff signature",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "date3",
        "question_text": "Date",
        "field_type": "date",
        "required": False
    })
    
    # Emergency information
    template.append({
        "id": "escalation_mechanism",
        "question_text": "Escalation mechanism in the event of emergency",
        "field_type": "textarea",
        "required": True
    })
    
    # Medication details section - First medication
    template.append({
        "id": "medication1_times",
        "question_text": "Time/s of Administration",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "medication1_name",
        "question_text": "Name of Medication",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "medication1_route",
        "question_text": "Route (e.g., oral, skin, gastrostomy)",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "medication1_dosage",
        "question_text": "Dosage",
        "field_type": "text",
        "required": True
    })
    
    # Medication details section - Second medication
    template.append({
        "id": "medication2_times",
        "question_text": "Time/s of Administration",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication2_name",
        "question_text": "Name of Medication",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication2_route",
        "question_text": "Route (e.g., oral, skin, gastrostomy)",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication2_dosage",
        "question_text": "Dosage",
        "field_type": "text",
        "required": False
    })
    
    # Medication details section - Third medication
    template.append({
        "id": "medication3_times",
        "question_text": "Time/s of Administration",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication3_name",
        "question_text": "Name of Medication",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication3_route",
        "question_text": "Route (e.g., oral, skin, gastrostomy)",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication3_dosage",
        "question_text": "Dosage",
        "field_type": "text",
        "required": False
    })
    
    # Medication details section - Fourth medication
    template.append({
        "id": "medication4_times",
        "question_text": "Time/s of Administration",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication4_name",
        "question_text": "Name of Medication",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication4_route",
        "question_text": "Route (e.g., oral, skin, gastrostomy)",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication4_dosage",
        "question_text": "Dosage",
        "field_type": "text",
        "required": False
    })
    
    # Medication details section - Fifth medication
    template.append({
        "id": "medication5_times",
        "question_text": "Time/s of Administration",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication5_name",
        "question_text": "Name of Medication",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication5_route",
        "question_text": "Route (e.g., oral, skin, gastrostomy)",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication5_dosage",
        "question_text": "Dosage",
        "field_type": "text",
        "required": False
    })
    
    # Medication details section - Sixth medication
    template.append({
        "id": "medication6_times",
        "question_text": "Time/s of Administration",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication6_name",
        "question_text": "Name of Medication",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication6_route",
        "question_text": "Route (e.g., oral, skin, gastrostomy)",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication6_dosage",
        "question_text": "Dosage",
        "field_type": "text",
        "required": False
    })
    
    # Medication details section - Seventh medication
    template.append({
        "id": "medication7_times",
        "question_text": "Time/s of Administration",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication7_name",
        "question_text": "Name of Medication",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication7_route",
        "question_text": "Route (e.g., oral, skin, gastrostomy)",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication7_dosage",
        "question_text": "Dosage",
        "field_type": "text",
        "required": False
    })
    
    # Medication details section - Eighth medication
    template.append({
        "id": "medication8_times",
        "question_text": "Time/s of Administration",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication8_name",
        "question_text": "Name of Medication",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication8_route",
        "question_text": "Route (e.g., oral, skin, gastrostomy)",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "medication8_dosage",
        "question_text": "Dosage",
        "field_type": "text",
        "required": False
    })
    
    # Week 1 - Medication Schedule
    template.append({
        "id": "week1_header",
        "question_text": "Week 1 Medication Schedule",
        "field_type": "header",
        "required": False
    })
    
    # First row - Day 1
    template.append({
        "id": "week1_day1_date",
        "question_text": "DD/MM/YY",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "week1_day1_time",
        "question_text": "Time",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week1_day1_initial",
        "question_text": "Staff Initial",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week1_day1_comment",
        "question_text": "Comment",
        "field_type": "text",
        "required": False
    })
    
    # Second row - Day 2
    template.append({
        "id": "week1_day2_date",
        "question_text": "DD/MM/YY",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "week1_day2_time",
        "question_text": "Time",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week1_day2_initial",
        "question_text": "Staff Initial",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week1_day2_comment",
        "question_text": "Comment",
        "field_type": "text",
        "required": False
    })
    
    # Third row - Day 3
    template.append({
        "id": "week1_day3_date",
        "question_text": "DD/MM/YY",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "week1_day3_time",
        "question_text": "Time",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week1_day3_initial",
        "question_text": "Staff Initial",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week1_day3_comment",
        "question_text": "Comment",
        "field_type": "text",
        "required": False
    })
    
    # Week 2 - Medication Schedule
    template.append({
        "id": "week2_header",
        "question_text": "Week 2 Medication Schedule",
        "field_type": "header",
        "required": False
    })
    
    # First row - Day 1
    template.append({
        "id": "week2_day1_date",
        "question_text": "DD/MM/YY",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "week2_day1_time",
        "question_text": "Time",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week2_day1_initial",
        "question_text": "Staff Initial",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week2_day1_comment",
        "question_text": "Comment",
        "field_type": "text",
        "required": False
    })
    
    # Second row - Day 2
    template.append({
        "id": "week2_day2_date",
        "question_text": "DD/MM/YY",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "week2_day2_time",
        "question_text": "Time",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week2_day2_initial",
        "question_text": "Staff Initial",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week2_day2_comment",
        "question_text": "Comment",
        "field_type": "text",
        "required": False
    })
    
    # Third row - Day 3
    template.append({
        "id": "week2_day3_date",
        "question_text": "DD/MM/YY",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "week2_day3_time",
        "question_text": "Time",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week2_day3_initial",
        "question_text": "Staff Initial",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "week2_day3_comment",
        "question_text": "Comment",
        "field_type": "text",
        "required": False
    })
    
    return template


def is_medication_administration_form(file_path_or_content: str) -> bool:
    """
    Determine if the file is likely a Medication Administration Form.
    
    Args:
        file_path_or_content: The path to the file or the content as a string
        
    Returns:
        bool: True if the file appears to be a medication administration form
    """
    try:
        content = ""
        
        # Check if the input is a file path
        if isinstance(file_path_or_content, str) and os.path.exists(file_path_or_content):
            # Check if it's a docx file
            if file_path_or_content.lower().endswith('.docx'):
                try:
                    # Try to use docx module to extract content
                    import docx
                    doc = docx.Document(file_path_or_content)
                    content = '\n'.join([para.text for para in doc.paragraphs])
                except Exception as e:
                    print(f"Error extracting docx content: {e}")
                    # Fallback to raw content
                    try:
                        with open(file_path_or_content, 'rb') as f:
                            raw_bytes = f.read()
                            content = raw_bytes.decode('utf-8', errors='ignore')
                    except Exception:
                        pass
            else:
                # Assume it's a text file or other readable format
                try:
                    with open(file_path_or_content, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    # Try binary mode if text mode fails
                    try:
                        with open(file_path_or_content, 'rb') as f:
                            raw_bytes = f.read()
                            content = raw_bytes.decode('utf-8', errors='ignore')
                    except Exception:
                        pass
        else:
            # Assume it's already content
            content = str(file_path_or_content)
            
        # Define keywords and patterns that indicate this is a medication administration form
        keywords = [
            r"medication\s+administration",
            r"participant",
            r"date\s+of\s+birth",
            r"support\s+worker",
            r"staff\s+signature",
            r"escalation\s+mechanism",
            r"administration",
            r"name\s+of\s+medication",
            r"route",
            r"dosage",
            r"staff\s+initial",
            r"comment"
        ]
        
        # Create a scoring system - if enough keywords are found, consider it a match
        score = 0
        for keyword in keywords:
            if re.search(keyword, content.lower()):
                score += 1
                print(f"Matched keyword: {keyword}")
                
        # If 4 or more keywords match, consider it a medication administration form
        print(f"Medication Form Detection Score: {score} out of {len(keywords)}")
        return score >= 4
        
    except Exception as e:
        # If there's any error in processing, default to False
        print(f"Error in is_medication_administration_form: {e}")
        return False