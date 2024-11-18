"""Topic categorization functionality for the quiz application."""
from typing import Dict, List

class TopicCategorizer:
    """Categorizes questions into topics based on content analysis."""
    
    def __init__(self):
        """Initialize topic keywords."""
        self.topics: Dict[str, List[str]] = {
            'Licensing': [
                'license', 'permit', 'renewal', 'application', 'fee',
                'valid', 'provisional', 'duplicate'
            ],
            'Rules and Regulations': [
                'law', 'legal', 'requirement', 'required', 'must',
                'penalty', 'consequence'
            ],
            'Road Signs': [
                'sign', 'signal', 'yield', 'turn', 'crossing',
                'arrow', 'warning', 'regulatory'
            ],
            'Safety': [
                'safety', 'accident', 'crash', 'emergency', 'caution',
                'danger', 'hazard', 'defensive'
            ],
            'Traffic Laws': [
                'traffic', 'speed', 'right of way', 'lane', 'merge',
                'stop', 'yield', 'passing'
            ],
            'Insurance': [
                'insurance', 'coverage', 'liability', 'no-fault',
                'policy', 'premium'
            ],
            'Violations': [
                'DUI', 'violation', 'suspended', 'revoked', 'ticket',
                'offense', 'penalty', 'fine'
            ],
            'Vehicle Operation': [
                'drive', 'driving', 'vehicle', 'operation', 'operate',
                'steering', 'brake', 'accelerate'
            ]
        }
    
    def categorize(self, question: str) -> str:
        """Categorize a question based on its content."""
        question_lower = question.lower()
        
        # Check each topic's keywords
        for topic, keywords in self.topics.items():
            if any(keyword.lower() in question_lower for keyword in keywords):
                return topic
        
        return "General Knowledge"
    
    def get_topics(self) -> List[str]:
        """Get list of all available topics."""
        return list(self.topics.keys()) + ["General Knowledge"]

# Create global topic categorizer instance
topic_categorizer = TopicCategorizer()
