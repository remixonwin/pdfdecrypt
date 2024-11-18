"""Quiz data loading and processing functionality."""
import csv
from pathlib import Path
import streamlit as st
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

def generate_explanation(question: str, correct_answer: str, topic: str) -> str:
    """Generate an explanation for the correct answer based on context"""
    
    # Common explanation patterns based on question type
    explanations = {
        'Licensing': {
            'pattern': r'(minimum|required|valid|fee)',
            'template': "According to Minnesota Driver's Manual, {} is the correct requirement for {}."
        },
        'Rules and Regulations': {
            'pattern': r'(must|required|legal|law)',
            'template': "Minnesota law states that {} regarding {}."
        },
        'Road Signs': {
            'pattern': r'sign|signal',
            'template': "This traffic control device indicates {}. It's important to {} for road safety."
        },
        'Safety': {
            'pattern': r'safety|emergency|caution',
            'template': "For safety reasons, {} is the correct action when {}."
        }
    }
    
    # Clean up the question and answer
    q_lower = question.lower()
    
    # Try to match topic-specific patterns
    if topic in explanations:
        pattern = explanations[topic]['pattern']
        if re.search(pattern, q_lower):
            # Extract relevant parts of the question
            context = re.sub(r'^what (is|should|must|does)|[?]', '', q_lower).strip()
            return explanations[topic]['template'].format(correct_answer, context)
    
    # Default explanation if no pattern matches
    return f"The correct answer is {correct_answer}. This is based on Minnesota driving regulations and safety guidelines."

def categorize_question(question: str) -> str:
    """Categorize questions based on content analysis"""
    # Define topic keywords
    topics = {
        'Licensing': ['license', 'permit', 'renewal', 'application', 'fee', 'valid', 'provisional', 'duplicate'],
        'Rules and Regulations': ['law', 'legal', 'requirement', 'required', 'must', 'penalty', 'consequence'],
        'Road Signs': ['sign', 'signal', 'yield', 'turn', 'crossing', 'arrow'],
        'Safety': ['safety', 'accident', 'crash', 'emergency', 'caution', 'danger'],
        'Traffic Laws': ['traffic', 'speed', 'right of way', 'lane', 'merge', 'stop'],
        'Insurance': ['insurance', 'coverage', 'liability', 'no-fault'],
        'Violations': ['DUI', 'violation', 'suspended', 'revoked', 'ticket', 'offense'],
        'Vehicle Operation': ['drive', 'driving', 'vehicle', 'operation', 'operate'],
    }
    
    # Convert question to lowercase for matching
    question_lower = question.lower()
    
    # Check each topic's keywords
    for topic, keywords in topics.items():
        if any(keyword.lower() in question_lower for keyword in keywords):
            return topic
    
    return "General Knowledge"

def validate_question(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Validate and clean question data."""
    try:
        # Clean all text fields
        question = clean_text(row.get('Question'))
        correct_answer = clean_text(row.get('Correct Answer'))
        options = [
            clean_text(row.get('Option A')),
            clean_text(row.get('Option B')),
            clean_text(row.get('Option C')),
            clean_text(row.get('Option D'))
        ]
        
        # Validate required fields silently
        if not question or not correct_answer:
            logger.error(f"Invalid question: Missing question or correct answer")
            return None
            
        # Remove empty options and ensure we have at least 2 options
        options = [opt for opt in options if opt]
        if len(options) < 2:
            logger.error(f"Invalid question: Not enough valid options")
            return None
            
        # Ensure correct answer is in options
        if correct_answer not in options:
            logger.error(f"Invalid question: Correct answer not in options")
            # Add correct answer to options if missing
            options.append(correct_answer)
            
        # Determine topic
        topic = categorize_question(question)
        
        return {
            'question': question,
            'options': options,
            'correct_answer': correct_answer,
            'topic': topic,
            'explanation': generate_explanation(question, correct_answer, topic)
        }
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return None

@st.cache_data
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