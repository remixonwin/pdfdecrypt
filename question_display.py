import streamlit as st
import random
import time
from typing import List, Tuple

def randomize_options(options: List[str], correct_answer: str) -> Tuple[List[str], str]:
    """Randomize options and return shuffled options with correct answer"""
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)
    return shuffled_options, correct_answer

def display_question(current_q: dict, question_num: int, total: int) -> None:
    """Display question, handle user input and scoring"""
    # Display current score at top
    score = st.session_state.score
    st.sidebar.metric("Current Score", f"{score}/{total} ({(score/total*100):.1f}%)")
    
    # Progress bar and question
    st.progress(question_num / total)
    st.subheader(f"Question {question_num + 1} of {total}")
    st.write(current_q['question'])
    
    # Get or generate shuffled options
    if f'options_{question_num}' not in st.session_state:
        shuffled, correct_answer = randomize_options(current_q['options'], current_q['correct_answer'])
        st.session_state[f'options_{question_num}'] = shuffled
        st.session_state[f'correct_{question_num}'] = correct_answer
        
    options = st.session_state[f'options_{question_num}']
    correct_answer = st.session_state[f'correct_{question_num}']
    
    # Navigation buttons
    col1, col2 = st.columns([1,4])
    with col1:
        if question_num > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_question -= 1
                st.rerun()
    
    # Answer selection
    user_answer = st.radio("Select your answer:", options, key=f"q_{question_num}")
    
    # Submit button and feedback
    if st.button("Submit", key=f"submit_{question_num}"):
        if user_answer == correct_answer:
            st.success("✅ Correct!")
            if question_num not in st.session_state.answered_correctly:
                st.session_state.score += 1
                st.session_state.answered_correctly.add(question_num)
                st.sidebar.metric("Current Score", f"{st.session_state.score}/{total} ({(st.session_state.score/total*100):.1f}%)")
            time.sleep(1.5)
        else:
            st.error(f"❌ Incorrect. The correct answer is: {correct_answer}")
            time.sleep(1.5)
        # Move to next question regardless of answer
        st.session_state.current_question += 1
        st.rerun()