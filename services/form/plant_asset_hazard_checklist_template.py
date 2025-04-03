"""
Template-based fallback solution for the New Plant-Asset Hazard Checklist form
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any
import os
import re


def get_plant_asset_hazard_checklist_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the New Plant-Asset Hazard Checklist form
    with the exact structure matching the document.
    """
    return [
        # General Information section
        {
            "id": "general_info_note",
            "question_text": "If "yes" is the answer to a question in the checklist, the plant, parts of the plant and/or the situation associated with the hazard should be written in the space provided.",
            "question_type": "information",
            "required": False,
            "options": []
        },
        {
            "id": "asset_name",
            "question_text": "Name of asset:",
            "question_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "asset_location",
            "question_text": "Location:",
            "question_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "assessor_name",
            "question_text": "Name of assessor:",
            "question_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "serial_number",
            "question_text": "Serial number:",
            "question_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "date_of_purchase",
            "question_text": "Date of Purchase:",
            "question_type": "date",
            "required": True,
            "options": []
        },
        {
            "id": "date_of_assessment",
            "question_text": "Date of assessment:",
            "question_type": "date",
            "required": True,
            "options": []
        },
        {
            "id": "owner_user",
            "question_text": "Owner/user of asset:",
            "question_type": "text",
            "required": True,
            "options": []
        },
        {
            "id": "date_of_handover",
            "question_text": "Date of handover:",
            "question_type": "date",
            "required": True,
            "options": []
        },
        # Entanglement section
        {
            "id": "entanglement_header",
            "question_text": "Entanglement",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "entanglement_q1",
            "question_text": "Can anyone's hair, clothing, gloves, necktie, jewellery, cleaning brushes, rags or other materials become entangled with moving parts of the plant, or materials in motion?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "entanglement_comments",
            "question_text": "Comments on entanglement hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Crushing section
        {
            "id": "crushing_header",
            "question_text": "Crushing",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "crushing_intro",
            "question_text": "Can anyone be crushed due to:",
            "question_type": "information",
            "required": False,
            "options": []
        },
        {
            "id": "crushing_q1",
            "question_text": "a. Material falling off the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "crushing_q2",
            "question_text": "b. Uncontrolled or unexpected movement of the plant or its load?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "crushing_q3",
            "question_text": "c. Lack of capacity for the plant to be slowed, stopped, or immobilised?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "crushing_q4",
            "question_text": "d. The plant tipping or rolling over?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "crushing_q5",
            "question_text": "e. Parts of the plant collapsing?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "crushing_comments",
            "question_text": "Comments on crushing hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Cutting, stabbing, and puncturing section
        {
            "id": "cutting_header",
            "question_text": "Cutting, stabbing, and puncturing",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "cutting_intro",
            "question_text": "Can anyone be cut, stabbed, or punctured due to:",
            "question_type": "information",
            "required": False,
            "options": []
        },
        {
            "id": "cutting_q1",
            "question_text": "a. Coming into contact with sharp or flying objects?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "cutting_q2",
            "question_text": "b. Coming into contact with moving parts of the plant during testing, inspection, operation, maintenance, cleaning, or repair of the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "cutting_q3",
            "question_text": "c. The plant, parts of the plant or work pieces disintegrating?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "cutting_q4",
            "question_text": "d. Work pieces being ejected?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "cutting_q5",
            "question_text": "e. The mobility of the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "cutting_q6",
            "question_text": "f. Uncontrolled or unexpected movement of the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "cutting_q7",
            "question_text": "g. Other factors not mentioned?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "cutting_comments",
            "question_text": "Comments on cutting, stabbing, and puncturing hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Shearing section
        {
            "id": "shearing_header",
            "question_text": "Shearing",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "shearing_q1",
            "question_text": "Can anyone's body parts be sheared between two parts of the plant, or between a part of the plant and a work piece or structure?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "shearing_comments",
            "question_text": "Comments on shearing hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Friction section
        {
            "id": "friction_header",
            "question_text": "Friction",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "friction_q1",
            "question_text": "Can anyone be burnt due to contact with moving parts or surfaces of the plant, or material handled by the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "friction_comments",
            "question_text": "Comments on friction hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Striking section
        {
            "id": "striking_header",
            "question_text": "Striking",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "striking_intro",
            "question_text": "Can anyone be struck by moving objects due to:",
            "question_type": "information",
            "required": False,
            "options": []
        },
        {
            "id": "striking_q1",
            "question_text": "a. Uncontrolled or unexpected movement of the plant or material handled by the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "striking_q2",
            "question_text": "b. The plant, parts of the plant or work pieces disintegrating?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "striking_q3",
            "question_text": "c. Work pieces being ejected?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "striking_q4",
            "question_text": "d. Mobility of the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "striking_q5",
            "question_text": "e. Other factors not mentioned?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "striking_comments",
            "question_text": "Comments on striking hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # High Pressure Fluid section
        {
            "id": "high_pressure_header",
            "question_text": "High Pressure Fluid",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "high_pressure_q1",
            "question_text": "Can anyone come into contact with fluids under high pressure, due to plant failure or misuse of the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "high_pressure_comments",
            "question_text": "Comments on high pressure fluid hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Electrical section
        {
            "id": "electrical_header",
            "question_text": "Electrical",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "electrical_intro",
            "question_text": "Can anyone be injured by electrical shock or burnt due to:",
            "question_type": "information",
            "required": False,
            "options": []
        },
        {
            "id": "electrical_q1",
            "question_text": "a. The plant contacting live electrical conductors?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "electrical_q2",
            "question_text": "b. The plant working within proximity to electrical conductors?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "electrical_q3",
            "question_text": "c. Overload of electrical circuits?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "electrical_q4",
            "question_text": "d. Damaged or poorly maintained electrical leads and cables?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "electrical_q5",
            "question_text": "e. Damaged electrical switches?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "electrical_q6",
            "question_text": "f. Water near electrical equipment?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "electrical_q7",
            "question_text": "g. Lack of isolation procedures?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "electrical_q8",
            "question_text": "h. Other factors not mentioned?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "electrical_comments",
            "question_text": "Comments on electrical hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Explosion section
        {
            "id": "explosion_header",
            "question_text": "Explosion",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "explosion_q1",
            "question_text": "Can anyone be injured by explosion of gases, vapours, liquids, dusts, or other substances triggered by the operation of the plant or material handled by the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "explosion_comments",
            "question_text": "Comments on explosion hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Tripping, slipping, and falling section
        {
            "id": "tripping_header",
            "question_text": "Tripping, slipping, and falling",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "tripping_q1",
            "question_text": "a. Uneven or slippery work surfaces?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "tripping_q2",
            "question_text": "b. Poor housekeeping, e.g., swarf in the vicinity of the plant, spillage not cleaned up?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "tripping_q3",
            "question_text": "c. Obstacles being placed in the vicinity of the plant?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "tripping_q4",
            "question_text": "d. Other factors not mentioned?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "falling_q1",
            "question_text": "a. Lack of a proper work platform?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "falling_q2",
            "question_text": "b. Lack of proper stairs or ladders?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "falling_q3",
            "question_text": "c. Lack of guardrails or other suitable edge protection?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "falling_q4",
            "question_text": "d. Unprotected holes, penetrations, or gaps?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "falling_q5",
            "question_text": "e. poor floor or walking surfaces, such as the lack of a slip-resistant surface?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "falling_q6",
            "question_text": "f. steep walking surfaces?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "falling_q7",
            "question_text": "g. Collapse of the supporting structure?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "falling_q8",
            "question_text": "h. Other factors not mentioned?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "tripping_comments",
            "question_text": "Comments on tripping, slipping, and falling hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Ergonomic section
        {
            "id": "ergonomic_header",
            "question_text": "Ergonomic",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "ergonomic_q1",
            "question_text": "a. Poorly designed seating?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "ergonomic_q2",
            "question_text": "b. Repetitive body movement?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "ergonomic_q3",
            "question_text": "c. Constrained body posture or the need for excessive effort?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "ergonomic_q4",
            "question_text": "d. Design deficiency causing mental or psychological stress?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "ergonomic_q5",
            "question_text": "e. Inadequate or poorly placed lighting?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "ergonomic_q6",
            "question_text": "f. Lack of consideration given to human error or human behaviour?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "ergonomic_q7",
            "question_text": "g. Other factors not mentioned?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "ergonomic_comments",
            "question_text": "Comments on ergonomic hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Suffocation section
        {
            "id": "suffocation_header",
            "question_text": "Suffocation",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "suffocation_q1",
            "question_text": "Can anyone be suffocated due to lack of oxygen, or atmospheric contamination?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "suffocation_comments",
            "question_text": "Comments on suffocation hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # High temperature or fire section
        {
            "id": "high_temp_header",
            "question_text": "High temperature or fire",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "high_temp_q1",
            "question_text": "Can anyone come into contact with objects at high temperature?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "high_temp_comments",
            "question_text": "Comments on high temperature hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Temperature (thermal comfort) section
        {
            "id": "temp_comfort_header",
            "question_text": "Temperature (thermal comfort)",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "temp_comfort_q1",
            "question_text": "Can anyone suffer ill health due to exposure to high or low temperatures?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "temp_comfort_comments",
            "question_text": "Comments on temperature comfort hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Other hazards section
        {
            "id": "other_hazards_header",
            "question_text": "Other hazards",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "other_hazards_intro",
            "question_text": "Can anyone be injured or suffer ill health from exposure to:",
            "question_type": "information",
            "required": False,
            "options": []
        },
        {
            "id": "other_hazards_q1",
            "question_text": "a. Chemicals?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "other_hazards_q2",
            "question_text": "b. Toxic gases or vapours?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "other_hazards_q3",
            "question_text": "c. Fumes?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "other_hazards_q4",
            "question_text": "d. Dust?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "other_hazards_q5",
            "question_text": "e. Noise?",
            "question_type": "radio",
            "required": True,
            "options": ["Yes", "No", "NA"]
        },
        {
            "id": "other_hazards_comments",
            "question_text": "Comments on other hazards:",
            "question_type": "textarea",
            "required": False,
            "options": []
        },
        # Corrective Action section
        {
            "id": "corrective_action_header",
            "question_text": "Corrective Action",
            "question_type": "header",
            "required": False,
            "options": []
        },
        {
            "id": "corrective_action",
            "question_text": "Action",
            "question_type": "textarea",
            "required": False,
            "options": []
        }
    ]


def is_plant_asset_hazard_checklist(file_path_or_content: str) -> bool:
    """
    Determine if the file is likely a New Plant-Asset Hazard Checklist.
    
    Args:
        file_path_or_content: The path to the file or its content
        
    Returns:
        bool: True if the file appears to be a plant-asset hazard checklist
    """
    # Check if the input is a file path or content
    if os.path.exists(file_path_or_content):
        # It's a file path
        file_path = file_path_or_content
        # Check filename first
        filename = os.path.basename(file_path).lower()
        if "plant-asset" in filename or "plant_asset" in filename or "new plant" in filename:
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
    
    # Check content for key phrases that indicate it's a plant-asset hazard checklist
    content_lower = content.lower()
    
    # Check for specific sections and unique phrases from the Plant-Asset Hazard Checklist
    indicators = [
        "plant-asset hazard checklist",
        "new plant-asset hazard checklist",
        "plant, parts of the plant and/or the situation associated with the hazard",
        # Check for multiple sections from the checklist
        "entanglement" in content_lower and "crushing" in content_lower and "shearing" in content_lower,
        # Check for specific questions unique to this form
        "can anyone's hair, clothing, gloves, necktie, jewellery" in content_lower,
        "can anyone be crushed due to" in content_lower and "material falling off the plant" in content_lower
    ]
    
    # Return True if any indicator is found
    return any(indicator == True or (isinstance(indicator, str) and indicator in content_lower) for indicator in indicators)