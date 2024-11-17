import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random
import time
import csv
import io

@st.cache_data
def load_quiz_data() -> Dict[str, List[dict]]:
    """Load quiz data from CSV and convert to proper format"""
    quiz_data = {}
    csv_path = Path("Minnesota_Driving_Quiz.csv")
    
    try:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            questions = []
            for row in reader:
                # Format question data with correct answer first
                options = [
                    row['Correct Answer'],  # Put correct answer first
                    row['Option A'] if row['Option A'] != row['Correct Answer'] else row['Option B'],
                    row['Option B'] if row['Option B'] != row['Correct Answer'] else row['Option C'],
                    row['Option C'] if row['Option C'] != row['Correct Answer'] else row['Option D']
                ]
                # Remove duplicates and ensure 4 unique options
                options = list(dict.fromkeys(options))[:4]
                
                question = {
                    'question': row['Question'],
                    'options': options,
                    'correct_answer': row['Correct Answer']
                }
                questions.append(question)
            
            # Group questions into sections of 10
            for i in range(0, len(questions), 10):
                section = f"Section {i//10 + 1}"
                quiz_data[section] = questions[i:i+10]
                
    except Exception as e:
        st.error(f"Error reading quiz data: {str(e)}")
    
    return quiz_data

def randomize_options(options: List[str]) -> Tuple[List[str], str]:
    """Randomize options and return shuffled options with correct answer"""
    correct_answer = options[0]  # Store correct answer
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)
    return shuffled_options, correct_answer

def init_session_state(defaults: Dict) -> None:
    """Initialize session state variables"""
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_question(current_q: dict, question_num: int, total: int) -> None:
    st.progress(question_num / total)
    st.subheader(f"Question {question_num + 1} of {total}")
    st.write(current_q['question'])
    
    # Get or generate shuffled options
    if f'options_{question_num}' not in st.session_state:
        shuffled = current_q['options'].copy()
        random.shuffle(shuffled)
        st.session_state[f'options_{question_num}'] = shuffled
        
    options = st.session_state[f'options_{question_num}']
    correct_answer = current_q['correct_answer']
    
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
            time.sleep(1.5)
            st.session_state.current_question += 1
            st.rerun()
        else:
            st.error(f"❌ Incorrect. The correct answer is: {correct_answer}")

def main():
    st.set_page_config(page_title="Driver's Manual Quiz", page_icon="🚗")
    st.title("Minnesota Driver's Manual Quiz")
    
    init_session_state({
        'score': 0,
        'current_question': 0,
        'questions': [],
        'current_section': None,
        'answered_correctly': set()
    })
    
    quiz_data = load_quiz_data()
    if not quiz_data:
        st.error("No quiz data found. Please check the data directory.")
        return
    
    if st.button("Start New Quiz"):
        section = random.choice(list(quiz_data.keys()))
        st.session_state.current_section = section
        st.session_state.questions = quiz_data[section]
        st.session_state.score = 0
        st.session_state.current_question = 0
        st.session_state.answered_correctly = set()
        # Clear previous question options
        for key in list(st.session_state.keys()):
            if key.startswith('options_') or key.startswith('correct_'):
                del st.session_state[key]
        st.rerun()

    if st.session_state.current_section:
        st.subheader(f"Current Section: {st.session_state.current_section}")

    if st.session_state.questions:
        total_questions = len(st.session_state.questions)
        current_q_idx = st.session_state.current_question

        if current_q_idx < total_questions:
            current_q = st.session_state.questions[current_q_idx]
            display_question(current_q, current_q_idx, total_questions)
        else:
            score = st.session_state.score
            st.success(f"Quiz completed! Score: {score}/{total_questions} ({score/total_questions*100:.1f}%)")
            if st.button("Restart Quiz"):
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.current_section = None
                st.session_state.answered_correctly = set()
                st.rerun()
    else:
        st.info("Please start a new quiz to begin.")

if __name__ == "__main__":
    main()