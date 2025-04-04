"""
Template-based fallback solution for the Mealtime Food Safety Audit Checklist
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any
import re
import os
import docx

def get_mealtime_safety_audit_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Mealtime Food Safety Audit Checklist
    with the exact structure matching the document.
    """
    template = []
    
    # Site Information section
    template.append({
        "id": "q_address",
        "question_text": "Site Information: Address:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "q_assessment_date",
        "question_text": "Date of assessment:",
        "field_type": "date",
        "required": True
    })
    
    template.append({
        "id": "q_evaluator",
        "question_text": "Name of evaluator:",
        "field_type": "text",
        "required": True
    })
    
    template.append({
        "id": "q_other_info",
        "question_text": "Any other information:",
        "field_type": "textarea",
        "required": False
    })
    
    # Compliance section
    template.append({
        "id": "q_staff_aware_food_safety",
        "question_text": "Staff aware of the food safety issues?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_staff_aware_mealtime_plans",
        "question_text": "Staff aware of the mealtime management plans?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_staff_aware_food_hygiene",
        "question_text": "Are staff aware of food hygiene",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_mealtime_policy_available",
        "question_text": "Mealtime management policy and procedure is available and communicated?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_risk_assessment_completed",
        "question_text": "Individual Risk Assessment Form is completed and documented?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_nutrition_swallowing_completed",
        "question_text": "Nutrition and Swallowing Risk Checklist is completed and documented?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_nutrition_assessment_completed",
        "question_text": "Nutrition Assessment is completed and documented?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    # Labelling and traceability section
    template.append({
        "id": "q_stored_foods_labelled",
        "question_text": "Stored foods are clearly labelled with name, and use by date?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    # Storage section
    template.append({
        "id": "q_packed_foods_condition",
        "question_text": "Packed foods are in good condition?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_sufficient_storage",
        "question_text": "Is there sufficient storage space?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_storage_temperatures",
        "question_text": "Are temperatures of the storage areas operating in the correct range?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_cross_contamination",
        "question_text": "Are foods stored to prevent cross contamination? (e.g., galleries) Are foods free from allergens stored so that they cannot be contaminated by foods containing allergens?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_refrigeration_calibrated",
        "question_text": "Are refrigeration appliances calibrated on a regular basis?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    # Cleaning section
    template.append({
        "id": "q_cleaning_schedules",
        "question_text": "Are the cleaning schedules completed regularly?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_sanitisers_available",
        "question_text": "Are sanitisers for work surfaces readily available for use during food preparation?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_cleaning_equipment",
        "question_text": "is the cleaning equipment clean, in good repair and stored appropriately after use?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_chemicals_stored",
        "question_text": "Are all cleaning chemicals store separately from food areas?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_chemicals_labelled",
        "question_text": "Are all cleaning chemicals in clearly labelled containers?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_sds_available",
        "question_text": "Are SDS readily available?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    # Pest Control section
    template.append({
        "id": "q_no_pest_evidence",
        "question_text": "There is no evidence of pest or rodent activity",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_bait_station_map",
        "question_text": "There is a map of all bait stations",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_msds_pest_control",
        "question_text": "There is a record of all MSDS for all pest control chemicals used",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_pest_activity_actions",
        "question_text": "Have actions been taken and recorded when there has been evidence of pest activity?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    # Waste section
    template.append({
        "id": "q_waste_removal",
        "question_text": "Waste is removed when bins are ¾ full",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_waste_bins_identifiable",
        "question_text": "Are waste disposal bins identifiable from food storage bins?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_waste_containers_clean",
        "question_text": "Waste containers are covered, kept clean and emptied after each work period",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    # Personal Hygiene section
    template.append({
        "id": "q_hygiene_monitored",
        "question_text": "Daily hygiene practices are monitored by the Co-ordinator and all corrective actions completed",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_handwashing_facilities",
        "question_text": "There are sufficient hand-washing facilities installed in all food handling areas",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_handwashing_frequency",
        "question_text": "Food handlers wash their hands as often as necessary",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_gloves_usage",
        "question_text": "Food handlers use gloves appropriately and correctly",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_jewellery_removed",
        "question_text": "All jewellery including watches is removed prior to commencing direct food handling",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_no_eating_smoking",
        "question_text": "There is no evidence of eating or smoking in food preparation areas",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_protective_clothing",
        "question_text": "Kitchen personnel wear appropriate protective clothing and protective head coverings",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_sick_staff_excluded",
        "question_text": "Sick staff are excluded from working with food",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_first_aid_wounds",
        "question_text": "There is a First-Aid box available/ wounds are covered with coloured, waterproof dressings",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    # Service section
    template.append({
        "id": "q_serving_times_monitored",
        "question_text": "Are serving times and temperatures satisfactory and monitored by staff?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_corrective_actions",
        "question_text": "Have appropriate corrective actions been taken where problems have occurred?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_prevent_contamination",
        "question_text": "Are all necessary steps taken to prevent the likelihood of food being contaminated during the serving process?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_food_covered",
        "question_text": "Is food covered wherever possible while being plated and served?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    template.append({
        "id": "q_clean_crockery",
        "question_text": "Are all items of crockery and cutlery clean prior to use?",
        "field_type": "radio",
        "options": ["Yes", "No", "NA"],
        "required": True
    })
    
    # Other criteria section (empty fields for custom criteria)
    for i in range(1, 10):
        template.append({
            "id": f"q_other_criteria_{i}",
            "question_text": f"Other criteria {i}",
            "field_type": "text",
            "required": False
        })
    
    # Corrective Action table
    template.append({
        "id": "q_corrective_actions_table",
        "question_text": "Corrective Action",
        "field_type": "table",
        "columns": ["Action", "Who is responsible", "Due date", "Completed"],
        "rows": 4,
        "required": False
    })
    
    return template


def is_mealtime_safety_audit(file_path_or_content: str) -> bool:
    """
    Determine if the file is likely a Mealtime Food Safety Audit Checklist.
    
    Args:
        file_path_or_content: The path to the file or the content as a string
        
    Returns:
        bool: True if the file appears to be a mealtime food safety audit checklist
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
            
        # Define keywords and patterns that indicate this is a mealtime food safety audit checklist
        keywords = [
            r"mealtime\s+food\s+safety\s+audit",
            r"staff\s+aware\s+of\s+food\s+safety",
            r"nutrition\s+and\s+swallowing\s+risk\s+checklist",
            r"mealtime\s+management\s+policy",
            r"pest\s+control",
            r"cleaning\s+schedules",
            r"personal\s+hygiene",
            r"corrective\s+action"
        ]
        
        # Create a scoring system - if enough keywords are found, consider it a match
        score = 0
        for keyword in keywords:
            if re.search(keyword, content.lower()):
                score += 1
                
        # If more than 3 keywords match, consider it a mealtime food safety audit checklist
        return score >= 3
        
    except Exception:
        # If there's any error in processing, default to False
        return False