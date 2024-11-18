"""Quiz utilities and core functionality."""
import streamlit as st
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from pathlib import Path

from quiz_loader import load_quiz_data as load_csv_quiz_data

def load_quiz_data():
    """Load quiz data from CSV file."""
    try:
        quiz_data = load_csv_quiz_data()
        if not quiz_data:
            st.error("No questions found in the quiz bank.")
            return []
        return quiz_data
    except Exception as e:
        st.error(f"Error loading quiz data: {str(e)}")
        return []

def load_user_progress():
    """Load user's question history and progress."""
    try:
        progress_file = Path("user_progress.json")
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                return json.load(f)
        return {'correct_questions': [], 'incorrect_questions': []}
    except Exception as e:
        st.error(f"Error loading progress: {str(e)}")
        return {'correct_questions': [], 'incorrect_questions': []}

def save_user_progress(progress):
    """Save user's question history and progress."""
    try:
        with open("user_progress.json", 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        st.error(f"Error saving progress: {str(e)}")

def initialize_quiz_state():
    """Initialize or reset quiz state."""
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    if 'score' not in st.session_state:
        st.session_state.score = 0
    
    if 'questions' not in st.session_state:
        questions = load_quiz_data()
        if questions:
            st.session_state.questions = questions
            # Shuffle questions for variety
            random.shuffle(st.session_state.questions)
        else:
            st.error("Failed to load quiz questions. Please check the quiz data file.")
            st.session_state.questions = []

def get_current_question():
    """Get the current question based on quiz state."""
    if not hasattr(st.session_state, 'questions') or not st.session_state.questions:
        return None
    
    if st.session_state.current_question >= len(st.session_state.questions):
        return None
        
    return st.session_state.questions[st.session_state.current_question]

def handle_answer(question_data: Dict[str, Any], user_answer: str):
    """Process user's answer and update progress."""
    progress = load_user_progress()
    correct = user_answer == question_data['correct_answer']
    
    if correct:
        st.session_state.score += 1
        if question_data['question'] not in progress['correct_questions']:
            progress['correct_questions'].append(question_data['question'])
    else:
        if question_data['question'] not in progress['incorrect_questions']:
            progress['incorrect_questions'].append(question_data['question'])
    
    save_user_progress(progress)
    st.session_state.current_question += 1
    return correct

def handle_error_report(question_data: Dict[str, Any], user_report: str, contact_email: Optional[str] = None):
    """Handle submission of error report."""
    try:
        send_error_report(question_data, user_report, contact_email)
        return True
    except Exception as e:
        st.error(f"Error submitting report: {str(e)}")
        return False

def get_quiz_summary():
    """Generate summary of quiz performance."""
    total_questions = len(st.session_state.questions)
    score = st.session_state.score
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    return {
        'total_questions': total_questions,
        'score': score,
        'percentage': percentage
    }

def reset_quiz():
    """Reset quiz state for a new attempt."""
    if 'questions' in st.session_state:
        random.shuffle(st.session_state.questions)
    st.session_state.current_question = 0
    st.session_state.score = 0

def send_error_report(question_data: dict, user_report: str, contact_email: str = None):
    """Send error report via email using Gmail SMTP."""
    try:
        # Create report content
        report_content = f"""
        Question: {question_data['question']}
        Options: {', '.join(question_data['options'])}
        Correct Answer: {question_data['correct_answer']}
        User Report: {user_report}
        Contact Email: {contact_email if contact_email else 'Not provided'}
        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Log the error report
        with open('error_reports.log', 'a') as f:
            f.write(f"\n{'='*50}\n{report_content}\n")
            
        return True
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        return False

def display_score(total_questions, min_correct):
    current_score = st.session_state.score
    questions_remaining = total_questions - st.session_state.current_question
    max_possible_score = current_score + questions_remaining
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Score", f"{current_score}/{total_questions}")
    with col2:
        st.metric("Required to Pass", f"{min_correct}/{total_questions}")
    with col3:
        st.metric("Current Percentage", f"{(current_score/total_questions*100):.1f}%")
        
    if max_possible_score < min_correct:
        st.warning("⚠️ Cannot achieve passing score of 80%")
    elif current_score >= min_correct:
        st.success("🎉 Passing score achieved!")

def handle_quiz_end(total_questions, min_correct, pass_percentage):
    score = st.session_state.score
    percentage = (score/total_questions*100)
    passed = score >= min_correct
    
    if passed:
        st.success(f"🎉 Congratulations! You passed with {score}/{total_questions} ({percentage:.1f}%)")
    else:
        st.error(f"❌ Quiz failed. Score: {score}/{total_questions} ({percentage:.1f}%). Required: {pass_percentage}%")
    
    # Show bookmarked questions first
    if hasattr(st.session_state, 'bookmarked_questions') and st.session_state.bookmarked_questions:
        st.subheader("📑 Bookmarked Questions")
        for q_num in st.session_state.bookmarked_questions:
            question = st.session_state.questions[q_num]
            with st.expander(f"Question {q_num + 1}: {question['question']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    if f'answered_{q_num}' in st.session_state and st.session_state[f'answered_{q_num}']:
                        st.write("Your Answer:", st.session_state[f'user_answer_{q_num}'])
                    st.write("Correct Answer:", question['correct_answer'])
                with col2:
                    st.write("Topic:", question['topic'])
                
                st.markdown("---")
                st.markdown("### Explanation")
                st.write(question['explanation'])
                st.info(f"📚 Study Tip: Review the section on {question['topic']} in the Minnesota Driver's Manual.")
    
    # Then show incorrect answers
    if st.session_state.incorrect_questions:
        st.subheader("❌ Review Incorrect Answers")
        for idx, question in enumerate(st.session_state.incorrect_questions):
            with st.expander(f"Question {idx + 1}: {question['question']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Your Answer:", question['user_answer'])
                    st.write("Correct Answer:", question['correct_answer'])
                with col2:
                    st.write("Topic:", question['topic'])
                
                st.markdown("---")
                st.markdown("### Explanation")
                st.write(question['explanation'])
                st.info(f"📚 Study Tip: Review the section on {question['topic']} in the Minnesota Driver's Manual.")
    
    # Add practice mode option for bookmarked questions
    if hasattr(st.session_state, 'bookmarked_questions') and st.session_state.bookmarked_questions:
        if st.button("Practice Bookmarked Questions"):
            # Create a new quiz with only bookmarked questions
            st.session_state.practice_mode = True
            st.session_state.practice_questions = [
                st.session_state.questions[q_num] for q_num in st.session_state.bookmarked_questions
            ]
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answered_correctly = set()
            st.session_state.incorrect_questions = []
            st.rerun()
    
    # Regular restart option
    if st.button("Restart Quiz"):
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answered_correctly = set()
        st.session_state.incorrect_questions = []
        st.session_state.practice_mode = False
        st.rerun()

def save_score(score, total_questions):
    st.session_state.history.append({
        'score': score,
        'total_questions': total_questions,
        'percentage': (score / total_questions) * 100
    })

def display_history():
    if st.session_state.history:
        st.sidebar.subheader("Quiz History")
        for idx, entry in enumerate(st.session_state.history):
            st.sidebar.write(f"Quiz {idx + 1}: {entry['score']}/{entry['total_questions']} ({entry['percentage']:.1f}%)")

def start_new_quiz(quiz_data, total_questions):
    selected_questions = random.sample(quiz_data, total_questions)
    st.session_state.questions = selected_questions
    st.session_state.score = 0
    st.session_state.current_question = 0
    st.session_state.answered_correctly = set()
    st.session_state.incorrect_questions = []
    
    # Clear previous question options
    for key in list(st.session_state.keys()):
        if key.startswith('options_') or key.startswith('correct_'):
            del st.session_state[key]