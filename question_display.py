import streamlit as st
import time
from typing import List, Tuple

def randomize_options(options: List[str], correct_answer: str) -> Tuple[List[str], str]:
    """Randomize the order of options while keeping track of correct answer"""
    import random
    # Create a list of tuples (option, is_correct)
    option_pairs = [(opt, opt == correct_answer) for opt in options]
    # Shuffle the pairs
    random.shuffle(option_pairs)
    # Unzip the pairs
    shuffled_options = [pair[0] for pair in option_pairs]
    # Find the new position of correct answer
    new_correct = next(opt for opt in shuffled_options if opt == correct_answer)
    return shuffled_options, new_correct

def display_question(current_q: dict, question_num: int, total: int) -> None:
    """Display question, handle user input and scoring"""
    # Display current score at top
    score = st.session_state.score
    st.sidebar.metric("Current Score", f"{score}/{total} ({(score/total*100):.1f}%)")
    
    # Progress bar and question
    st.progress(question_num / total)
    st.subheader(f"Question {question_num + 1} of {total}")
    
    # Create columns for question and topic
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(current_q['question'])
    with col2:
        st.caption(f"Topic: {current_q['topic']}")
    
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
    
    # Track if question has been answered
    if f'answered_{question_num}' not in st.session_state:
        st.session_state[f'answered_{question_num}'] = False
    
    # Submit button and feedback
    if st.button("Submit", key=f"submit_{question_num}") and not st.session_state[f'answered_{question_num}']:
        st.session_state[f'answered_{question_num}'] = True
        
        if user_answer == correct_answer:
            st.success("✅ Correct!")
            # Show explanation in success box
            with st.expander("See Explanation", expanded=True):
                st.write(current_q['explanation'])
            
            if question_num not in st.session_state.answered_correctly:
                st.session_state.score += 1
                st.session_state.answered_correctly.add(question_num)
                st.sidebar.metric("Current Score", f"{st.session_state.score}/{total} ({(st.session_state.score/total*100):.1f}%)")
        else:
            st.error(f"❌ Incorrect. The correct answer is: {correct_answer}")
            # Show explanation in error box
            with st.expander("See Explanation", expanded=True):
                st.write(current_q['explanation'])
            
            # Store incorrect answer for review
            incorrect_question = {
                'question': current_q['question'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'explanation': current_q['explanation'],
                'topic': current_q['topic']
            }
            if not any(q['question'] == current_q['question'] for q in st.session_state.incorrect_questions):
                st.session_state.incorrect_questions.append(incorrect_question)
    
    # Show Next Question button only after answering
    if st.session_state[f'answered_{question_num}']:
        col1, col2 = st.columns([4,1])
        with col2:
            if st.button("Next ➡️", key=f"next_{question_num}"):
                st.session_state.current_question += 1
                st.rerun()