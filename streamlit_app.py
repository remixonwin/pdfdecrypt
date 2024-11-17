import streamlit as st
import random
from quiz_loader import load_quiz_data
from session_state import init_session_state
from question_display import display_question
from quiz_utils import start_new_quiz, display_score, handle_quiz_end, save_score, display_history

def main():
    st.set_page_config(page_title="Driver's Manual Quiz", page_icon="🚗")
    st.title("Minnesota Driver's Manual Quiz")
    
    # Constants for quiz parameters
    TOTAL_QUESTIONS = 40
    PASS_PERCENTAGE = 80
    MIN_CORRECT = int(TOTAL_QUESTIONS * PASS_PERCENTAGE / 100)
    
    init_session_state({
        'score': 0,
        'current_question': 0,
        'questions': [],
        'answered_correctly': set(),
        'history': []
    })
    
    quiz_data = load_quiz_data()
    if not quiz_data:
        st.error("No quiz data found. Please check the data directory.")
        return
    
    if len(quiz_data) < TOTAL_QUESTIONS:
        st.error(f"Not enough questions in the quiz data. Found {len(quiz_data)} questions, but need at least {TOTAL_QUESTIONS}.")
        return
    
    if st.button("Start New Quiz"):
        start_new_quiz(quiz_data, TOTAL_QUESTIONS)
        st.rerun()

    # Display current score and passing requirements
    if st.session_state.questions:
        display_score(TOTAL_QUESTIONS, MIN_CORRECT)
        
        current_q_idx = st.session_state.current_question
        if current_q_idx < TOTAL_QUESTIONS:
            current_q = st.session_state.questions[current_q_idx]
            display_question(current_q, current_q_idx, TOTAL_QUESTIONS)
        else:
            handle_quiz_end(TOTAL_QUESTIONS, MIN_CORRECT, PASS_PERCENTAGE)
            save_score(st.session_state.score, TOTAL_QUESTIONS)
    else:
        st.info("Please start a new quiz to begin.")
    
    # Display quiz history
    display_history()

if __name__ == "__main__":
    main()
