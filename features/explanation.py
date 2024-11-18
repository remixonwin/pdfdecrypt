"""Explanation generation functionality for the quiz application."""
import re
from typing import Dict, Pattern

class ExplanationGenerator:
    """Generates explanations for quiz questions based on topics."""
    
    def __init__(self):
        """Initialize explanation templates and patterns."""
        self.topic_templates: Dict[str, Dict[str, str | Pattern]] = {
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
            },
            'Traffic Laws': {
                'pattern': r'speed|right.of.way|lane|merge|stop',
                'template': "The traffic law states that {} when {}."
            },
            'Vehicle Operation': {
                'pattern': r'drive|driving|vehicle|operate|control',
                'template': "When operating a vehicle, {} is the correct procedure for {}."
            }
        }
    
    def generate(self, question: str, correct_answer: str, topic: str) -> str:
        """Generate an explanation for the given question and answer."""
        # Clean up the question and answer
        q_lower = question.lower()
        
        # Try to match topic-specific patterns
        if topic in self.topic_templates:
            pattern = self.topic_templates[topic]['pattern']
            if re.search(pattern, q_lower):
                # Extract relevant parts of the question
                context = re.sub(r'^what (is|should|must|does)|[?]', '', q_lower).strip()
                return self.topic_templates[topic]['template'].format(correct_answer, context)
        
        # Default explanation if no pattern matches
        return f"The correct answer is {correct_answer}. This is based on Minnesota driving regulations and safety guidelines."

# Create global explanation generator instance
explanation_generator = ExplanationGenerator()
