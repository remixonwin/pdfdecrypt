import csv
from pathlib import Path
import streamlit as st
from typing import List
import re

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

@st.cache_data
def load_quiz_data() -> List[dict]:
    """Load quiz data from CSV and convert to proper format"""
    quiz_data = []
    csv_path = Path("Minnesota_Driving_Quiz.csv")
    
    try:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Determine topic first for explanation generation
                    topic = categorize_question(row['Question'])
                    
                    # Format question data
                    question = {
                        'question': row['Question'],
                        'options': [row['Option A'], row['Option B'], row['Option C'], row['Option D']],
                        'correct_answer': row['Correct Answer'],
                        'topic': topic,
                        'explanation': generate_explanation(row['Question'], row['Correct Answer'], topic)
                    }
                    # Ensure options are properly formatted
                    question['options'] = [opt.strip() if opt is not None else '' for opt in question['options']]
                    # Ensure correct answer is properly formatted
                    question['correct_answer'] = question['correct_answer'].strip() if question['correct_answer'] is not None else ''
                    quiz_data.append(question)
                except KeyError as e:
                    st.error(f"Missing or incorrect key in CSV data: {str(e)}")
    except Exception as e:
        st.error(f"Error reading quiz data: {str(e)}")
    
    return quiz_data