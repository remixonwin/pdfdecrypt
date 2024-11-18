"""Quiz data loading and processing functionality."""
import csv
from pathlib import Path
import logging
import unicodedata
from typing import List, Dict, Any, Optional
import re

# Set up logging
logging.basicConfig(
    level=logging.ERROR,
    filename='quiz_errors.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text: Optional[str]) -> str:
    """Clean and validate text input."""
    if text is None:
        return ""
    
    # Fix common encoding issues
    text = text.strip()
    
    # Replace problematic characters
    replacements = {
        'â€™': "'",
        'â€"': "–",
        'â€œ': '"',
        'â€': '"',
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2013': "–",
        '\u2014': "—"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    return text

def remove_duplicates_from_csv():
    """Remove duplicate questions from the quiz bank."""
    try:
        # Read all questions
        questions = []
        seen_questions = set()
        duplicates_found = False
        
        with open("Minnesota_Driving_Quiz.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            
            # First row is headers
            questions.append(",".join(headers))
            
            for row in reader:
                # Clean the question text
                question = clean_text(row['Question']).lower().strip()
                
                # If we haven't seen this question before, add it
                if question not in seen_questions:
                    seen_questions.add(question)
                    # Preserve the original format with quotes and commas
                    row_values = [
                        f'"{row["Question"]}"' if ',' in row["Question"] else row["Question"],
                        row["Option A"],
                        row["Option B"],
                        row["Option C"],
                        row["Option D"],
                        row["Correct Answer"]
                    ]
                    questions.append(",".join(row_values))
                else:
                    duplicates_found = True
                    print(f"Duplicate found: {row['Question']}")
        
        if duplicates_found:
            # Write back the deduplicated questions
            with open("Minnesota_Driving_Quiz.csv", 'w', encoding='utf-8', newline='') as file:
                for line in questions:
                    file.write(line + '\n')
            
            return True, "Duplicates removed successfully"
        
        return False, "No duplicates found"
        
    except Exception as e:
        print(f"Error removing duplicates: {str(e)}")
        return False, f"Error: {str(e)}"

def load_quiz_data() -> List[dict]:
    """Load quiz data from CSV and convert to proper format"""
    quiz_data = []
    csv_path = Path("Minnesota_Driving_Quiz.csv")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                validated_question = validate_question(row)
                if validated_question is not None:
                    quiz_data.append(validated_question)
                
    except Exception as e:
        logger.error(f"Error reading quiz data: {str(e)}")
        # Return default questions if loading fails
        return [
            {
                'question': 'What is the default speed limit in a residential area?',
                'options': ['30 mph', '25 mph', '35 mph', '40 mph'],
                'correct_answer': '30 mph',
                'topic': 'Speed Limits',
                'explanation': 'The default speed limit in a residential area is 30 mph unless otherwise posted.'
            }
        ]
    
    if not quiz_data:
        logger.error("No valid questions loaded")
        return [
            {
                'question': 'What is the default speed limit in a residential area?',
                'options': ['30 mph', '25 mph', '35 mph', '40 mph'],
                'correct_answer': '30 mph',
                'topic': 'Speed Limits',
                'explanation': 'The default speed limit in a residential area is 30 mph unless otherwise posted.'
            }
        ]
    
    return quiz_data

def validate_question(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Validate and clean question data."""
    try:
        # Clean all text fields
        question = clean_text(row.get('Question'))
        options = [
            clean_text(row.get('Option A', '')),
            clean_text(row.get('Option B', '')),
            clean_text(row.get('Option C', '')),
            clean_text(row.get('Option D', ''))
        ]
        correct_answer = clean_text(row.get('Correct Answer', ''))
        
        # Filter out empty options
        options = [opt for opt in options if opt]
        
        # Validate required fields
        if not question:
            logger.error(f"Missing question text")
            return None
            
        if not options or len(options) < 2:
            logger.error(f"Not enough valid options for question: {question}")
            return None
            
        if not correct_answer:
            logger.error(f"Missing correct answer for question: {question}")
            return None
            
        if correct_answer not in options:
            # Try to find the correct answer in the options (case-insensitive)
            correct_answer_lower = correct_answer.lower()
            matching_options = [opt for opt in options if opt.lower() == correct_answer_lower]
            if matching_options:
                correct_answer = matching_options[0]
            else:
                # Add correct answer to options if it's valid
                if correct_answer.strip():
                    options.append(correct_answer)
                else:
                    logger.error(f"Correct answer not found in options for question: {question}")
                    return None
            
        return {
            'question': question,
            'options': options,
            'correct_answer': correct_answer,
            'topic': 'General Knowledge'  # Default topic
        }
        
    except Exception as e:
        logger.error(f"Error validating question: {str(e)}")
        return None