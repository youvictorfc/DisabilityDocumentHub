"""
Template-based solution for incident forms
This module provides predefined field structures for common form types
to ensure consistent extraction even when AI-based extraction fails.
"""

import os
import logging
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger(__name__)

def get_incident_form_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for standard incident forms
    with the exact structure matching the Minto Disability Services incident form.
    """
    template = [
        {
            "question_text": "Type of incident",
            "field_type": "text",
            "required": True,
            "id": "incident_type"
        },
        {
            "question_text": "Is it a reportable incident?",
            "field_type": "radio",
            "options": ["Yes", "No"],
            "required": True,
            "id": "is_reportable"
        },
        {
            "question_text": "NDIS or any other authorities?",
            "field_type": "text",
            "required": False,
            "id": "authorities"
        },
        {
            "question_text": "Name of employee providing report",
            "field_type": "text",
            "required": True,
            "id": "employee_name"
        },
        {
            "question_text": "Names of witnesses if applicable",
            "field_type": "text",
            "required": False,
            "id": "witnesses"
        },
        {
            "question_text": "This report is about a (please circle):",
            "field_type": "radio",
            "options": ["Concern", "Change", "Incident"],
            "required": True,
            "id": "report_type"
        },
        {
            "question_text": "Date and time of when issue occurred or was noticed:",
            "field_type": "datetime",
            "required": True,
            "id": "incident_datetime"
        },
        {
            "question_text": "Location/ Address:",
            "field_type": "text",
            "required": True,
            "id": "location"
        },
        {
            "question_text": "Name of Client:",
            "field_type": "text",
            "required": True,
            "id": "client_name"
        },
        {
            "question_text": "Description of issue being reported: (sketch if required)",
            "field_type": "textarea",
            "required": True,
            "id": "description"
        },
        {
            "question_text": "Immediate action taken: (if taken)",
            "field_type": "textarea",
            "required": False,
            "id": "immediate_action"
        },
        {
            "question_text": "Suggested further action: (include suggestions for reducing or eliminating the issue & timelines)",
            "field_type": "textarea",
            "required": False,
            "id": "suggested_action"
        },
        {
            "question_text": "Reported to: (Name of Manager/Coordinator)",
            "field_type": "text",
            "required": True,
            "id": "reported_to"
        },
        {
            "question_text": "Date:",
            "field_type": "date",
            "required": True,
            "id": "report_date"
        },
        {
            "question_text": "Signed by:",
            "field_type": "text",
            "required": True,
            "id": "signature"
        },
        {
            "question_text": "Date:",
            "field_type": "date",
            "required": True,
            "id": "signature_date"
        },
        # Incident Investigation section
        {
            "question_text": "Date received at head office:",
            "field_type": "date",
            "required": False,
            "id": "received_date"
        },
        {
            "question_text": "Please circle:",
            "field_type": "radio",
            "options": ["Concern", "Change", "Incident"],
            "required": False,
            "id": "classification"
        },
        {
            "question_text": "Name of employee:",
            "field_type": "text",
            "required": False,
            "id": "employee_name_2"
        },
        {
            "question_text": "Name of client:",
            "field_type": "text",
            "required": False,
            "id": "client_name_2"
        },
        # Short-Term Responses section
        {
            "question_text": "Indicate action taken by Unit Manager/Coordinator: (include discussion & feedback with employee, client/carer) to resolve the issue or provide an interim resolution.",
            "field_type": "textarea",
            "required": False,
            "id": "manager_action"
        },
        {
            "question_text": "Signed by:",
            "field_type": "text",
            "required": False,
            "id": "manager_signature"
        },
        {
            "question_text": "Date:",
            "field_type": "date",
            "required": False,
            "id": "manager_date"
        },
        {
            "question_text": "Response Timeframe",
            "field_type": "radio",
            "options": ["Immediate", "Urgent"],
            "required": False,
            "id": "response_timeframe"
        },
        {
            "question_text": "Date:",
            "field_type": "date",
            "required": False,
            "id": "timeframe_date"
        },
        # Long-Term Responses section
        {
            "question_text": "If further action is required, outline this and include timelines for review/resolution:",
            "field_type": "textarea",
            "required": False,
            "id": "further_action"
        },
        {
            "question_text": "Manager/ Coordinator:",
            "field_type": "text",
            "required": False,
            "id": "manager_name"
        },
        {
            "question_text": "Signature:",
            "field_type": "text",
            "required": False,
            "id": "manager_signature_2"
        },
        {
            "question_text": "Date:",
            "field_type": "date",
            "required": False,
            "id": "long_term_date"
        },
        {
            "question_text": "Reported to the Health and Safety Committee:",
            "field_type": "text",
            "required": False,
            "id": "health_safety_report"
        }
    ]
    
    return template

def is_incident_form(content: str) -> bool:
    """
    Determine if the form content matches an incident form pattern.
    
    Args:
        content: The extracted text content from the form
        
    Returns:
        bool: True if the content appears to be an incident form
    """
    # Primary indicators - strongly suggest this is an incident form
    primary_indicators = [
        "incident form",
        "incident report",
        "type of incident",
        "reportable incident",
    ]
    
    # Secondary indicators - common in incident forms but may appear in other forms too
    secondary_indicators = [
        "names of witnesses",
        "immediate action taken",
        "date and time of when issue occurred",
        "description of issue being reported",
        "names of witnesses",
        "suggested further action",
        "ndis or any other authorities",
        "concern, change, incident",
        "name of employee providing report",
        "incident investigation",
        "health and safety committee"
    ]
    
    # Count how many indicators are present
    primary_count = sum(1 for indicator in primary_indicators if indicator.lower() in content.lower())
    secondary_count = sum(1 for indicator in secondary_indicators if indicator.lower() in content.lower())
    
    logger.debug(f"Incident form detection: {primary_count} primary and {secondary_count} secondary indicators found")
    
    # Rules to determine if it's an incident form:
    # 1. If at least 1 primary indicator is present AND at least 2 secondary indicators
    # 2. OR if at least 2 primary indicators are present
    # 3. OR if at least 4 secondary indicators are present (strong contextual evidence)
    is_incident = (primary_count >= 1 and secondary_count >= 2) or (primary_count >= 2) or (secondary_count >= 4)
    
    if is_incident:
        logger.info(f"Identified as incident form with {primary_count} primary and {secondary_count} secondary indicators")
    
    return is_incident