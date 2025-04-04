"""
Template-based fallback solution for the Nutrition and Swallowing Risk Checklist
This module provides a predefined field structure for the specific form
to ensure consistent extraction even when AI-based extraction fails.
"""

from typing import List, Dict, Any
import os
import re


def get_nutrition_swallowing_risk_template() -> List[Dict[str, Any]]:
    """
    Returns a predefined template for the Nutrition and Swallowing Risk Checklist
    with the exact structure matching the document.
    """
    return [
        {
            "id": "question_1",
            "question_text": "Question 1: If the person is a child, (i.e. under 18 years of age) have they lost weight or failed to gain weight over the last three months?",
            "field_type": "radio",
            "required": True,
            "options": ["Not applicable", "Yes", "No", "Unsure"]
        },
        {
            "id": "question_2",
            "question_text": "Question 2: Is the person underweight? Tick the 'Yes' box if either of the following apply: The person is an adult and their weight on the Weight for Height Chart is in the 'underweight' or 'very underweight' range; When you look carefully at the person (adult or child), their bone structure is easily defined under their skin. This can indicate significant loss of fat tissue and is easily checked by looking around the person's eyes and cheeks. Other areas to check include the shoulders, ribs and hips.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_3",
            "question_text": "Question 3: Has the person had unplanned weight loss or have they lost too much weight? Tick the 'Yes' box if any of the following apply: The person's weight loss is undesirable or has been unexpected; The person is under 18 years of age and there is weight loss in two or more consecutive months; The person has lost weight in two or more consecutive months and is not on a monitored weight loss program.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_4",
            "question_text": "Question 4: Is the person overweight? Tick the 'Yes' box if either of the following apply: The person is an adult (i.e. over 18 years of age) and their weight on the Weight for Height Chart is in the overweight or obese range; The person (adult or child) appears to have rolls of body fat.(e.g. around the abdomen)",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_5",
            "question_text": "Question 5: Has the person had unplanned weight gain or have they gained too much weight? Tick the 'Yes' box if either of the following apply: The person's weight gain is undesirable or has been unexpected; The person is not on a weight gain program and their clothes no longer fit.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_6",
            "question_text": "Question 6: Is the person receiving tube feeds? Tick the 'Yes' box if the person is receiving nasogastric, naso-duodenal or gastrostomy feeding.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_6a",
            "question_text": "Question 6a: If you answered 'Yes' to question 6, does the person also receive food or drink through the mouth? Tick the 'Yes' box if the person receives any food or drink by mouth, in addition to tube feeding. If the person is receiving tube feeds and no other food by mouth, then answer only questions 10, 13, 14, 16,18 and 19.",
            "field_type": "radio",
            "required": False,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_7",
            "question_text": "Question 7: Is the person physically dependent on others in order to eat or drink? Tick the 'Yes' box if: The person cannot put food or drink into their own mouth and someone else is needed to feed them; The person is dependent on assistance during a meal (e.g. guidance with utensils).",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_8",
            "question_text": "Question 8: Has the person had a reduction in appetite or food or fluid intake? Tick the 'Yes' box if either of the following apply: The person is not eating or drinking as much as they usually do and this is unintentional; The person appears unwilling to take most food offered to them and the equivalent of six large glasses of fluid each day.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_9",
            "question_text": "Question 9: Does the person follow, or are they supposed to follow, a special diet? Tick the 'Yes' box if they are on, or are supposed to be on, any of the following dietary plans: Pureed, minced, chopped or soft foods; Thickened fluids; Weight reduction or weight-increasing; Low fat; Vegetarian; Low cholesterol or cholesterol-lowering; Diabetic; Any other diet which modifies or restricts foods or food choices.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_10",
            "question_text": "Question 10: Does the person take multiple medications? Tick the 'Yes' box if: The person is usually on more than one type of medication.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_11",
            "question_text": "Question 11: Does the person select inappropriate foods or behave inappropriately with food? Tick the 'Yes' box if any of the following apply: The person over-consumes alcohol or coffee, tea and cola drinks; The person eats non-food items such as dirt, grass or faeces; The person drinks excessive amounts of fluid; The person steals or hides food.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_12",
            "question_text": "Question 12: Does the person usually exclude foods from any food group? Tick the 'Yes' box if the person usually excludes all foods from one or more of the following groups of food: Bread, cereals, rice, pasta, noodles; Vegetables, legumes; Fruit; Milk, yogurt, cheese; Meat, fish, poultry, eggs, nuts, legumes",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_13",
            "question_text": "Question 13: Does the person get constipated? Tick the 'Yes' box if either of the following apply: The person's bowel movements are irregular, painful and sometimes infrequent; Laxatives, suppositories or enemas are required to maintain regular bowel movements.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_14",
            "question_text": "Question 14: Does the person have frequent fluid-type bowel movements?",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_15",
            "question_text": "Question 15: Does the person have mouth or teeth problems that affect their eating? Tick the 'Yes' box if any of the following apply: The person's teeth are loose, broken or missing; The person's lips, tongue, throat or gums are red and inflamed or ulcerated; The person has a malocclusion (upper and lower teeth do not meet) and this affects their ability to chew",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_16",
            "question_text": "Question 16: Does the person suffer from frequent chest infections, pneumonia, asthma or wheezing? Tick the 'Yes' box if any of the following apply: The person has had frequent chest infections or pneumonia; The person is usually 'chesty' or has difficulty clearing phlegm; The person has asthma or wheezes.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_17",
            "question_text": "Question 17: Does the person cough, gag and choke or breathe noisily during or after eating food, drinking, or taking medication? Tick the 'Yes' box if any of the following apply: The person sometimes coughs or chokes during or several minutes after eating, drinking or taking medication; The person's breathing becomes noisy after eating or drinking or while talking; The person gags on eating, drinking or taking medication.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_18",
            "question_text": "Question 18: Does the person vomit or regurgitate on a regular basis? (Note: This question is not applicable to infants under 12 months of age) Tick the 'Yes' box if either: The person vomits or regurgitates (i.e. brings up) food, drink or medication more than once per day or on a regular basis; The person takes anti-reflux medication; The person clears their throat often or burps often.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_19",
            "question_text": "Question 19: Does the person drool or dribble saliva when resting, eating or drinking? Tick the 'Yes' box if either of the following apply: The person drools or dribbles saliva at rest or mealtimes; The person's clothes or protective napkins/bibs frequently need changing because of drooling.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_20",
            "question_text": "Question 20: Does food or drink fall out of the person's mouth during eating or drinking? Tick the 'Yes' box if any of the following apply: The person is unable to close their mouth and this causes food, drink or medication to fall out of their mouth; The person cannot keep their head upright and food, drink or medication falls out of their mouth; The person's tongue pushes food, drink or medication out of their mouth; The person's mouth continuously needs to be wiped or they need to wear a cloth to protect their clothes during mealtime. Note that this question does not relate to the person's manual dexterity or ability to place food in their mouth.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_21",
            "question_text": "Question 21: If the person eats independently, do they overfill their mouth or try to eat very quickly? Tick the 'Yes' box if the person eats independently and any of the following apply: The person tries to cram or 'stuff' their mouth before attempting to chew or swallow; The person tries to swallow too much food before they have chewed it properly; The person usually finishes all of their main meal in less than five minutes.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_22",
            "question_text": "Question 22: Does the person appear to eat without chewing? (Note: This question does not apply to people on a pureed diet) Tick the 'Yes' box if any of the following apply: The person sucks their food instead of chewing; The food remains in the person's mouth for a long period of time before being swallowed; The person swallows their food whole without chewing.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_23",
            "question_text": "Question 23: Does the person take a long time to eat their meals? Tick the 'Yes' box if any of the following apply: The person eats independently and they take more than 30 minutes to eat meals; The person is dependent on someone to feed them and it takes a long time to feed them the whole meal; The person appears to tire as the meal progresses and may not finish their meal.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "question_24",
            "question_text": "Question 24: Does the person show distress during or after eating or drinking? Tick the 'Yes' box if any of the following apply: The person appears distressed while they eat or drink; The person appears distressed immediately after or shortly after eating or drinking; Sometimes while distressed the person refuses food or spits out food.",
            "field_type": "radio",
            "required": True,
            "options": ["Yes", "No", "Unsure"]
        },
        {
            "id": "summary_comments",
            "question_text": "Comments",
            "field_type": "textarea",
            "required": False,
            "options": []
        },
        {
            "id": "further_action",
            "question_text": "Further Action Required (GP to complete)",
            "field_type": "textarea",
            "required": False,
            "options": []
        }
    ]


def is_nutrition_swallowing_risk(file_path: str) -> bool:
    """
    Determine if the file is likely a Nutrition and Swallowing Risk Checklist.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file appears to be a nutrition and swallowing risk checklist
    """
    try:
        # If it's a file path, read content
        if isinstance(file_path, str) and os.path.exists(file_path):
            try:
                import docx
                doc = docx.Document(file_path)
                content = ""
                for para in doc.paragraphs:
                    content += para.text + "\n"
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                content += paragraph.text + "\n"
                file_path = content
            except:
                # If we can't read as a docx, try to read as text
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_path = f.read()
                except:
                    pass
        
        # Check for key phrases that indicate it's a nutrition and swallowing risk checklist
        lower_content = file_path.lower()
        
        # Define key markers that strongly indicate this form
        key_markers = [
            "nutrition and swallowing risk",
            "weight loss",
            "weight gain",
            "tube feeds",
            "eating or drinking",
            "special diet",
            "multiple medications",
            "food group",
            "constipated",
            "mouth or teeth problems",
            "chest infections",
            "cough, gag and choke",
            "vomit or regurgitate",
            "drool or dribble"
        ]
        
        # Count how many key markers are found
        marker_count = sum(1 for marker in key_markers if marker in lower_content)
        
        # If at least 4 key markers are found, it's likely this form
        return marker_count >= 4
        
    except Exception as e:
        print(f"Error checking if document is a nutrition and swallowing risk checklist: {str(e)}")
        return False