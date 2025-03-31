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
            "question": "Type of incident",
            "type": "text",
            "required": True,
            "id": "incident_type"
        },
        {
            "question": "Is it a reportable incident?",
            "type": "radio",
            "options": ["Yes", "No"],
            "required": True,
            "id": "is_reportable"
        },
        {
            "question": "NDIS or any other authorities?",
            "type": "text",
            "required": False,
            "id": "authorities"
        },
        {
            "question": "Name of employee providing report",
            "type": "text",
            "required": True,
            "id": "employee_name"
        },
        {
            "question": "Names of witnesses if applicable",
            "type": "text",
            "required": False,
            "id": "witnesses"
        },
        {
            "question": "This report is about a (please circle):",
            "type": "radio",
            "options": ["Concern", "Change", "Incident"],
            "required": True,
            "id": "report_type"
        },
        {
            "question": "Date and time of when issue occurred or was noticed:",
            "type": "datetime",
            "required": True,
            "id": "incident_datetime"
        },
        {
            "question": "Location/ Address:",
            "type": "text",
            "required": True,
            "id": "location"
        },
        {
            "question": "Name of Client:",
            "type": "text",
            "required": True,
            "id": "client_name"
        },
        {
            "question": "Description of issue being reported: (sketch if required)",
            "type": "textarea",
            "required": True,
            "id": "description"
        },
        {
            "question": "Immediate action taken: (if taken)",
            "type": "textarea",
            "required": False,
            "id": "immediate_action"
        },
        {
            "question": "Suggested further action: (include suggestions for reducing or eliminating the issue & timelines)",
            "type": "textarea",
            "required": False,
            "id": "suggested_action"
        },
        {
            "question": "Reported to: (Name of Manager/Coordinator)",
            "type": "text",
            "required": True,
            "id": "reported_to"
        },
        {
            "question": "Date:",
            "type": "date",
            "required": True,
            "id": "report_date"
        },
        {
            "question": "Signed by:",
            "type": "text",
            "required": True,
            "id": "signature"
        },
        {
            "question": "Date:",
            "type": "date",
            "required": True,
            "id": "signature_date"
        },
        # Incident Investigation section
        {
            "question": "Date received at head office:",
            "type": "date",
            "required": False,
            "id": "received_date"
        },
        {
            "question": "Please circle:",
            "type": "radio",
            "options": ["Concern", "Change", "Incident"],
            "required": False,
            "id": "classification"
        },
        {
            "question": "Name of employee:",
            "type": "text",
            "required": False,
            "id": "employee_name_2"
        },
        {
            "question": "Name of client:",
            "type": "text",
            "required": False,
            "id": "client_name_2"
        },
        # Short-Term Responses section
        {
            "question": "Indicate action taken by Unit Manager/Coordinator: (include discussion & feedback with employee, client/carer) to resolve the issue or provide an interim resolution.",
            "type": "textarea",
            "required": False,
            "id": "manager_action"
        },
        {
            "question": "Signed by:",
            "type": "text",
            "required": False,
            "id": "manager_signature"
        },
        {
            "question": "Date:",
            "type": "date",
            "required": False,
            "id": "manager_date"
        },
        {
            "question": "Response Timeframe",
            "type": "radio",
            "options": ["Immediate", "Urgent"],
            "required": False,
            "id": "response_timeframe"
        },
        {
            "question": "Date:",
            "type": "date",
            "required": False,
            "id": "timeframe_date"
        },
        # Long-Term Responses section
        {
            "question": "If further action is required, outline this and include timelines for review/resolution:",
            "type": "textarea",
            "required": False,
            "id": "further_action"
        },
        {
            "question": "Manager/ Coordinator:",
            "type": "text",
            "required": False,
            "id": "manager_name"
        },
        {
            "question": "Signature:",
            "type": "text",
            "required": False,
            "id": "manager_signature_2"
        },
        {
            "question": "Date:",
            "type": "date",
            "required": False,
            "id": "long_term_date"
        },
        {
            "question": "Reported to the Health and Safety Committee:",
            "type": "text",
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
    incident_indicators = [
        "incident form",
        "incident report",
        "type of incident",
        "reportable incident",
        "names of witnesses",
        "immediate action taken"
    ]
    
    # Count how many indicators are present
    indicator_count = sum(1 for indicator in incident_indicators if indicator.lower() in content.lower())
    
    # If more than 2 indicators are present, it's likely an incident form
    return indicator_count >= 2