import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Optional

@st.cache_data
def load_quiz_data() -> Dict[str, List[dict]]:
    """Load quiz data with caching to prevent repeated file reads"""
    data_dir = Path("data")
    quiz_data = {}
    
    # Scan the data directory for JSON files
    for path in data_dir.glob("*.json"):
        section = path.stem.replace('_', ' ').title()  # Create a section name from the filename
        try:
            data = json.loads(path.read_text())
            if 'quizzes' in data and data['quizzes']:
                quiz_data[section] = data['quizzes'][0]['questions']
            else:
                st.warning(f"No quizzes found in {path.name}")
        except json.JSONDecodeError:
            st.error(f"Invalid JSON in {path.name}")
    
    return quiz_data

def init_session_state(defaults: Dict) -> None:
    """Initialize session state variables"""
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_question(current_q: dict, question_num: int) -> Optional[str]:
    """Display a single question and its options"""
    if not current_q:
        st.error("Question data is missing or invalid")
        return None
        
    st.subheader(f"Question {question_num + 1}")
    st.write(current_q['question'])
    return st.radio(
        "Select your answer:", 
        current_q['options'], 
        key=f"q_{question_num}",
        help="Choose the best answer"
    )

def main():
    st.set_page_config(page_title="Driver's Manual Quiz", page_icon="🚗")
    st.title("Minnesota Driver's Manual Quiz")
    
    # Initialize state with type hints
    init_session_state({
        'score': 0,
        'current_question': 0,
        'questions': [],
        'selected_section': None
    })
    
    quiz_data = load_quiz_data()
    if not quiz_data:
        st.error("No quiz data found. Please check the data directory.")
        return
        
    # Persist section selection
    section = st.selectbox(
        "Select Quiz Section:", 
        list(quiz_data.keys()),
        key='selected_section'
    )
    
    if st.button("Start New Quiz"):
        st.session_state.questions = quiz_data[section]
        st.session_state.score = 0
        st.session_state.current_question = 0
        st.rerun()
    
    if not st.session_state.questions:
        st.info("Please start a new quiz to begin.")
        return

    total_questions = len(st.session_state.questions)
    current_q_idx = st.session_state.current_question

    if current_q_idx < total_questions:
        current_q = st.session_state.questions[current_q_idx]
        user_answer = display_question(current_q, current_q_idx)
        
        # Progress bar
        st.progress(current_q_idx / total_questions)
        
        if st.button("Next Question"):
            if user_answer == current_q['options'][0]:
                st.session_state.score += 1
            st.session_state.current_question += 1
            st.rerun()
    else:
        score = st.session_state.score
        st.success(f"Quiz completed! Your score: {score}/{total_questions} ({score/total_questions*100:.1f}%)")
        if st.button("Restart Quiz"):
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.rerun()

if __name__ == "__main__":
    main()