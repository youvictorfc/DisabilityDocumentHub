"""
Template-based fallback solution for the Nutrition Assessment form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any
import re
import os

def get_nutrition_assessment_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Nutrition Assessment form
    with the exact structure matching the document.
    """
    template = []
    
    # Assessor Information
    template.append({
        "id": "assessor_name",
        "question_text": "The assessment is prepared by: Name:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "assessor_contact",
        "question_text": "Contact detail:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "assessor_position",
        "question_text": "Position and profession:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "assessment_date",
        "question_text": "Date:",
        "field_type": "date",
        "required": True
    })
    
    # Participant Details
    template.append({
        "id": "participant_name",
        "question_text": "Participant Details: Name:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "ndis_number",
        "question_text": "NDIS number:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "plan_dates",
        "question_text": "Plan Dates:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "dob",
        "question_text": "DOB:",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "gender",
        "question_text": "Gender:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "address",
        "question_text": "Address:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "state",
        "question_text": "State:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "email",
        "question_text": "Email Address:",
        "field_type": "email",
        "required": True
    })
    
    template.append({
        "id": "phone",
        "question_text": "Phone:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "preferred_contact",
        "question_text": "Preferred Contact Person:",
        "field_type": "text",
        "required": True
    })
    
    # Personal Health History
    template.append({
        "id": "childhood_illness",
        "question_text": "Childhood illness:",
        "field_type": "checkbox",
        "options": ["Measles", "Mumps", "Rubella", "Chickenpox", "Rheumatic Fever", "Polio"],
        "required": False
    })
    
    template.append({
        "id": "immunizations",
        "question_text": "Immunizations and dates:",
        "field_type": "checkbox",
        "options": ["Tetanus", "Pneumonia", "Hepatitis", "Chickenpox", "Influenza", "MMR Measles, Mumps, Rubella"],
        "required": False
    })
    
    template.append({
        "id": "tetanus_date",
        "question_text": "Tetanus date:",
        "field_type": "date",
        "required": False
    })
    
    template.append({
        "id": "pneumonia_date",
        "question_text": "Pneumonia date:",
        "field_type": "date",
        "required": False
    })
    
    template.append({
        "id": "hepatitis_date",
        "question_text": "Hepatitis date:",
        "field_type": "date",
        "required": False
    })
    
    template.append({
        "id": "chickenpox_date",
        "question_text": "Chickenpox date:",
        "field_type": "date",
        "required": False
    })
    
    template.append({
        "id": "influenza_date",
        "question_text": "Influenza date:",
        "field_type": "date",
        "required": False
    })
    
    template.append({
        "id": "mmr_date",
        "question_text": "MMR date:",
        "field_type": "date",
        "required": False
    })
    
    template.append({
        "id": "medical_problems",
        "question_text": "List any medical problems that other doctors have diagnosed:",
        "field_type": "textarea",
        "required": False
    })
    
    # Surgeries
    template.append({
        "id": "surgeries",
        "question_text": "Surgeries:",
        "field_type": "table",
        "columns": ["Year", "Reason", "Hospital"],
        "rows": 4,
        "required": False
    })
    
    # Other hospitalizations
    template.append({
        "id": "hospitalizations",
        "question_text": "Other hospitalizations and Major Illnesses:",
        "field_type": "table",
        "columns": ["Year", "Reason", "Hospital"],
        "rows": 4,
        "required": False
    })
    
    # Medications
    template.append({
        "id": "medications",
        "question_text": "List your prescribed drugs and over-the-counter drugs, such as vitamins and inhalers:",
        "field_type": "table",
        "columns": ["Name the Drug", "Strength", "Frequency Taken"],
        "rows": 6,
        "required": False
    })
    
    # Health Habits And Personal Safety
    template.append({
        "id": "exercise",
        "question_text": "Exercise:",
        "field_type": "radio",
        "options": [
            "Sedentary (No exercise)", 
            "Mild exercise (i.e., climb stairs, walk 3 blocks, golf)", 
            "Occasional vigorous exercise (i.e., work or recreation, less than 4x/week for 30 min.)", 
            "Regular vigorous exercise (i.e., work or recreation 4x/week for 30 minutes)"
        ],
        "required": False
    })
    
    template.append({
        "id": "weight_loss_success",
        "question_text": "Have you had success in previous weight loss?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "weight_loss_reason",
        "question_text": "What was the reason?",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "dieting",
        "question_text": "Are you dieting?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "medical_diet",
        "question_text": "If yes, are you on a physician prescribed medical diet?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "meals_per_day",
        "question_text": "# Of meals you eat in an average day?",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "salt_intake",
        "question_text": "Rank salt intake:",
        "field_type": "radio",
        "options": ["Hi", "Med", "Low"],
        "required": False
    })
    
    template.append({
        "id": "fat_intake",
        "question_text": "Rank fat intake:",
        "field_type": "radio",
        "options": ["Hi", "Med", "Low"],
        "required": False
    })
    
    template.append({
        "id": "caffeine",
        "question_text": "Caffeine:",
        "field_type": "checkbox",
        "options": ["None", "Coffee", "Tea", "Cola"],
        "required": False
    })
    
    template.append({
        "id": "cups_per_day",
        "question_text": "# Of cups/cans per day?",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "alcohol",
        "question_text": "Do you drink alcohol?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "alcohol_kind",
        "question_text": "If yes, what kind?",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "drinks_per_week",
        "question_text": "How many drinks per week?",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "alcohol_concern",
        "question_text": "Are you concerned about the amount you drink?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "considered_stopping",
        "question_text": "Have you considered stopping?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "blackouts",
        "question_text": "Have you ever experienced blackouts?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "binge_drinking",
        "question_text": "Are you prone to \"binge\" drinking?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "drive_after_drinking",
        "question_text": "Do you drive after drinking?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "tobacco",
        "question_text": "Do you use tobacco?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "tobacco_type",
        "question_text": "Tobacco type:",
        "field_type": "checkbox",
        "options": ["Cigarettes", "Chew", "Pipe", "Cigars"],
        "required": False
    })
    
    template.append({
        "id": "tobacco_amount",
        "question_text": "Tobacco amount/frequency:",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "tobacco_years",
        "question_text": "# Of years using tobacco:",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "quit_year",
        "question_text": "Or year quit:",
        "field_type": "text",
        "required": False
    })
    
    template.append({
        "id": "recreational_drugs",
        "question_text": "Do you currently use recreational or street drugs?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "needle_drugs",
        "question_text": "Have you ever given yourself street drugs with a needle?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "live_alone",
        "question_text": "Do you live alone?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "frequent_falls",
        "question_text": "Do you have frequent falls?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "vision_hearing_loss",
        "question_text": "Do you have vision or hearing loss?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    template.append({
        "id": "advance_directive",
        "question_text": "Do you have an Advance Directive or Living Will?",
        "field_type": "radio",
        "options": ["Yes", "No"],
        "required": False
    })
    
    # Mental Health section
    template.append({
        "id": "mental_health",
        "question_text": "Mental Health",
        "field_type": "textarea",
        "required": False
    })
    
    # Personal Hygiene section
    template.append({
        "id": "personal_hygiene",
        "question_text": "Personal Hygiene",
        "field_type": "textarea",
        "required": False
    })
    
    # Continence Management section
    template.append({
        "id": "continence_management",
        "question_text": "Continence Management",
        "field_type": "textarea",
        "required": False
    })
    
    # Sensory section
    template.append({
        "id": "sensory",
        "question_text": "Sensory",
        "field_type": "textarea",
        "required": False
    })
    
    # Pain Management section
    template.append({
        "id": "pain_management",
        "question_text": "Pain Management",
        "field_type": "textarea",
        "required": False
    })
    
    # Behaviour Management section
    template.append({
        "id": "behaviour_management",
        "question_text": "Behaviour Management",
        "field_type": "textarea",
        "required": False
    })
    
    # Other Problem section
    template.append({
        "id": "other_problem",
        "question_text": "Other Problem",
        "field_type": "textarea",
        "required": False
    })
    
    return template


def is_nutrition_assessment(file_path_or_content: str) -> bool:
    """
    Determine if the file is likely a Nutrition Assessment form.
    
    Args:
        file_path_or_content: The path to the file or the content as a string
        
    Returns:
        bool: True if the file appears to be a nutrition assessment form
    """
    try:
        content = ""
        
        # Check if the input is a file path
        if os.path.exists(file_path_or_content):
            # Assume it's a text file or already content
            with open(file_path_or_content, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        else:
            # Assume it's already content
            content = file_path_or_content
            
        # Define keywords and patterns that indicate this is a nutrition assessment form
        keywords = [
            r"nutrition\s+assessment",
            r"participant\s+details",
            r"personal\s+health\s+history",
            r"surgeries",
            r"health\s+habits\s+and\s+personal\s+safety",
            r"mental\s+health",
            r"personal\s+hygiene",
            r"continence\s+management"
        ]
        
        # Create a scoring system - if enough keywords are found, consider it a match
        score = 0
        for keyword in keywords:
            if re.search(keyword, content.lower()):
                score += 1
                
        # If 3 or more keywords match, consider it a nutrition assessment form
        return score >= 3
        
    except Exception:
        # If there's any error in processing, default to False
        return False