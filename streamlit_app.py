import streamlit as st
import random
import time
from quiz_loader import load_quiz_data
from session_state import init_session_state
from question_display import display_question

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
        'answered_correctly': set()
    })
    
    quiz_data = load_quiz_data()
    if not quiz_data:
        st.error("No quiz data found. Please check the data directory.")
        return
    
    if len(quiz_data) < TOTAL_QUESTIONS:
        st.error(f"Not enough questions in the quiz data. Found {len(quiz_data)} questions, but need at least {TOTAL_QUESTIONS}.")
        return
    
    if st.button("Start New Quiz"):
        # Randomly select 40 questions
        selected_questions = random.sample(quiz_data, TOTAL_QUESTIONS)
        
        st.session_state.questions = selected_questions
        st.session_state.score = 0
        st.session_state.current_question = 0
        st.session_state.answered_correctly = set()
        
        # Clear previous question options
        for key in list(st.session_state.keys()):
            if key.startswith('options_') or key.startswith('correct_'):
                del st.session_state[key]
        st.rerun()

    # Display current score and passing requirements
    if st.session_state.questions:
        current_score = st.session_state.score
        questions_remaining = TOTAL_QUESTIONS - st.session_state.current_question
        max_possible_score = current_score + questions_remaining
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Score", f"{current_score}/{TOTAL_QUESTIONS}")
        with col2:
            st.metric("Required to Pass", f"{MIN_CORRECT}/{TOTAL_QUESTIONS}")
        with col3:
            st.metric("Current Percentage", f"{(current_score/TOTAL_QUESTIONS*100):.1f}%")
            
        # Calculate and show if passing is still possible
        if max_possible_score < MIN_CORRECT:
            st.warning("⚠️ Cannot achieve passing score of 80%")
        elif current_score >= MIN_CORRECT:
            st.success("🎉 Passing score achieved!")

        current_q_idx = st.session_state.current_question
        if current_q_idx < TOTAL_QUESTIONS:
            current_q = st.session_state.questions[current_q_idx]
            display_question(current_q, current_q_idx, TOTAL_QUESTIONS)
        else:
            score = st.session_state.score
            percentage = (score/TOTAL_QUESTIONS*100)
            passed = score >= MIN_CORRECT
            
            if passed:
                st.success(f"🎉 Congratulations! You passed with {score}/{TOTAL_QUESTIONS} ({percentage:.1f}%)")
            else:
                st.error(f"❌ Quiz failed. Score: {score}/{TOTAL_QUESTIONS} ({percentage:.1f}%). Required: {PASS_PERCENTAGE}%")
            
            if st.button("Restart Quiz"):
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.answered_correctly = set()
                st.rerun()
    else:
        st.info("Please start a new quiz to begin.")

if __name__ == "__main__":
    main()
