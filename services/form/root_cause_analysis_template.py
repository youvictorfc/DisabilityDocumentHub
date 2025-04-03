"""
Template-based fallback solution for the Root Cause Analysis Form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any
import os
import re


def get_root_cause_analysis_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Root Cause Analysis Form
    with the exact structure matching the document.
    """
    return [
        # Participant Information section
        {
            "id": "participant_file_id",
            "question_text": "Participant File ID:",
            "field_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "participant_dob",
            "question_text": "Participant DOB:",
            "field_type": "date",
            "required": True,
            "options": []
        },
        {
            "id": "program_facility",
            "question_text": "Program/Facility:",
            "field_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "gender",
            "question_text": "Gender:",
            "field_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "location_of_event",
            "question_text": "Location of event:",
            "field_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "date_of_event",
            "question_text": "Date of Event:",
            "field_type": "date",
            "required": True,
            "options": []
        },
        {
            "id": "date_rca_completed",
            "question_text": "Date RCA Completed:",
            "field_type": "date",
            "required": True,
            "options": []
        },
        {
            "id": "staff_participated",
            "question_text": "Name of staff participated in RCA:",
            "field_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "rca_team_leader",
            "question_text": "RCA team leader name:",
            "field_type": "text",
            "required": True,
            "options": []
        },
        # The Event section
        {
            "id": "event_section",
            "question_text": "1. THE EVENT – Describe what happened and any harm that resulted. Identify the proximate cause, if known.",
            "field_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "rca_team_members",
            "question_text": "RCA Team Members:",
            "field_type": "textarea",
            "required": True,
            "options": []
        },
        {
            "id": "team_leader",
            "question_text": "Team Leader:",
            "field_type": "text",
            "required": True,
            "options": []
        },
        # Background & Factors section
        {
            "id": "background_section",
            "question_text": "2. BACKGROUND & FACTORS SUMMARY– Answer the following questions (brief summary only- attach supporting documents).",
            "field_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "expected_sequence",
            "question_text": "2.1 What was the sequence of events that was expected to take place?",
            "field_type": "textarea",
            "required": True,
            "options": []
        },
        {
            "id": "deviation_from_sequence",
            "question_text": "2.2 Was there a deviation from the expected sequence?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No"]
        },
        {
            "id": "deviation_description",
            "question_text": "If YES, describe the deviation.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "deviation_contributed",
            "question_text": "2.3 Was any deviation from the expected sequence likely to have led to or contributed to the adverse event?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "deviation_contribution_description",
            "question_text": "If YES, describe with causal statement.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "sequence_documented",
            "question_text": "2.4 Was the expected sequence described in policy, procedure, written guidelines, or included in staff training?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "sequence_source",
            "question_text": "If YES, cite source.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "sequence_meets_requirements",
            "question_text": "2.5 Does the expected sequence or process meet regulatory requirements and/or practice standards?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "sequence_deviation_description",
            "question_text": "If NO, describe deviation from requirements/standards.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "human_action_contributed",
            "question_text": "2.6 Did human action or inaction appear to contribute to the adverse event?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "human_action_description",
            "question_text": "If YES, describe the actions and how they contributed.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "equipment_contributed",
            "question_text": "2.7 Did a defect, malfunction, misuse of, or absence of equipment appear to contribute to the event?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "equipment_description",
            "question_text": "If YES, describe what equipment and how it appeared to contribute.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "usual_location",
            "question_text": "2.8 Was the procedure or activity involved in the event being carried out in the usual location?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "location_description",
            "question_text": "If NO, describe where and why a different location was utilised.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "regular_staff",
            "question_text": "2.9 Was the procedure or activity being carried out by regular staff familiar with the participant and activity?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "staff_description",
            "question_text": "If NO, describe who was carrying out the activity and why regular staff were not involved.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "staff_credentialed",
            "question_text": "2.10 Were involved staff credentialed/skilled to carry out the tasks expected of them?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "credential_inadequacy",
            "question_text": "If NO, describe the perceived inadequacy.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "staff_trained",
            "question_text": "2.11 Were staff trained to carry out their respective responsibilities?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "training_inadequacy",
            "question_text": "If NO, describe the perceived inadequacy.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "staffing_levels",
            "question_text": "2.12 Were staffing levels considered to have been adequate at the time of the incident?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "staffing_levels_description",
            "question_text": "If NO, describe why.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "other_staffing_factors",
            "question_text": "2.13 Were there other staffing factors identified as responsible for or contributing to the adverse event?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "other_staffing_factors_description",
            "question_text": "If YES, describe those factors.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "inaccurate_information",
            "question_text": "2.14 Did inaccurate or ambiguous information contribute to or cause the adverse event?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "inaccurate_information_description",
            "question_text": "If YES, describe what information and how it contributed.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "communication_lack",
            "question_text": "2.15 Did a lack of communication or incomplete communication contribute to or cause the adverse event?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "communication_lack_description",
            "question_text": "If YES, describe who and what and how it contributed.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "environmental_factors",
            "question_text": "2.16 Did any environmental factors contribute to or cause the adverse event?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "environmental_factors_description",
            "question_text": "If YES, describe what factors and how they contributed.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "organisational_factors",
            "question_text": "2.17 Did any organisational or leadership factors contribute to or cause the adverse event.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "organisational_factors_description",
            "question_text": "If YES, describe what factors and how they contributed.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "assessment_factors",
            "question_text": "2.18 Did any assessment or planning factors contribute to or cause the adverse event?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "assessment_factors_description",
            "question_text": "If YES, describe what factors and how they contributed.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "other_relevant_factors",
            "question_text": "2.19 What other factors are considered relevant to the adverse event?",
            "field_type": "textarea",
            "required": True,
            "options": []
        },
        {
            "id": "factor_ranking",
            "question_text": "2.20 Rank order the factors considered responsible for the adverse event, beginning with the proximate cause, followed by the most important to less important contributory factors. Attach Contributory Factors Diagram, if available.",
            "field_type": "textarea",
            "required": True,
            "options": []
        },
        {
            "id": "root_cause_identified",
            "question_text": "Was a root cause identified?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No"]
        },
        {
            "id": "root_cause_description",
            "question_text": "If YES, describe the root cause.",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "action_plan_section",
            "question_text": "3. ACTION PLAN (address the factors identified above. Prioritise actions based on risk scores. Consider alternatives if a preferable action cannot be taken at this time.)",
            "field_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "actions_to_address_section",
            "question_text": "Action/s to address identified factors. Specify factors, actions, action owner/s, and target dates:",
            "field_type": "textarea",
            "required": True,
            "options": []
        },
        {
            "id": "measurement_plan",
            "question_text": "3.1 Plan to measure the effectiveness of any action/s to be taken in response to the RCA findings:",
            "field_type": "textarea",
            "required": True,
            "options": []
        },
        {
            "id": "review_date",
            "question_text": "Date for evaluation of effectiveness of actions:",
            "field_type": "date",
            "required": True,
            "options": []
        },
        {
            "id": "report_forward",
            "question_text": "Forward this report to all RCA team members and to the following individuals:",
            "field_type": "textarea",
            "required": True,
            "options": []
        }
    ]


def is_root_cause_analysis_form(file_path_or_content: str) -> bool:
    """
    Determine if the file is likely a Root Cause Analysis Form.
    
    Args:
        file_path_or_content: The path to the file or its content
        
    Returns:
        bool: True if the file appears to be a Root Cause Analysis Form
    """
    # Check if the input is a file path or content
    if os.path.exists(file_path_or_content):
        # It's a file path
        file_path = file_path_or_content
        # Check filename first
        filename = os.path.basename(file_path).lower()
        if "root cause" in filename or "rca" in filename:
            return True
            
        # If not determined by filename, try to check content
        try:
            # For DOCX files
            if file_path.lower().endswith('.docx'):
                try:
                    import docx
                    doc = docx.Document(file_path)
                    content = " ".join([para.text for para in doc.paragraphs])
                except:
                    # If python-docx fails, we can't determine from content
                    return False
            # For other text-based files
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
        except:
            # If we can't read the file, we can't determine from content
            return False
    else:
        # It's content
        content = file_path_or_content
    
    # Check content for key phrases that indicate it's a Root Cause Analysis Form
    content_lower = content.lower()
    
    # Check for specific sections and phrases from the Root Cause Analysis Form
    indicators = [
        "root cause analysis form",
        "rca team leader",
        "the event – describe what happened",
        "background & factors summary",
        "was there a deviation from the expected sequence",
        "rank order the factors considered responsible"
    ]
    
    # Return True if any indicator is found
    return any(indicator in content_lower for indicator in indicators)