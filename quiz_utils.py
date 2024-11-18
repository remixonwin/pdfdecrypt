"""Quiz utilities and core functionality."""
import streamlit as st
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from features.error_reporting import error_reporter
from features.bookmarking import bookmark_manager
from features.explanation import explanation_generator
from features.topic_categorizer import topic_categorizer

def initialize_quiz_state():
    """Initialize quiz-related session state variables."""
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'answered_correctly' not in st.session_state:
        st.session_state.answered_correctly = set()
    if 'incorrect_questions' not in st.session_state:
        st.session_state.incorrect_questions = []
    if 'practice_mode' not in st.session_state:
        st.session_state.practice_mode = False

def get_current_question() -> Optional[Dict[str, Any]]:
    """Get the current question based on quiz state."""
    if st.session_state.practice_mode and hasattr(st.session_state, 'practice_questions'):
        questions = st.session_state.practice_questions
    elif hasattr(st.session_state, 'questions'):
        questions = st.session_state.questions
    else:
        return None
    
    if 0 <= st.session_state.current_question < len(questions):
        return questions[st.session_state.current_question]
    return None

def handle_answer(selected_answer: str, question_data: Dict[str, Any]) -> bool:
    """Process user's answer and update quiz state."""
    is_correct = selected_answer == question_data['correct_answer']
    current_q = st.session_state.current_question
    
    if is_correct:
        st.session_state.score += 1
        st.session_state.answered_correctly.add(current_q)
    else:
        st.session_state.incorrect_questions.append({
            'question': question_data['question'],
            'user_answer': selected_answer,
            'correct_answer': question_data['correct_answer']
        })
    
    return is_correct

def handle_error_report(question_data: Dict[str, Any], user_report: str, contact_email: Optional[str] = None) -> Tuple[bool, str]:
    """Handle submission of error report."""
    try:
        return error_reporter.send_error_report(question_data, user_report, contact_email)
    except Exception as e:
        st.error(f"Failed to send error report: {str(e)}")
        return False, "Error report could not be sent. Please try again later."

def get_quiz_summary() -> Dict[str, Any]:
    """Generate summary of quiz performance."""
    total_questions = len(st.session_state.questions)
    return {
        'score': st.session_state.score,
        'total': total_questions,
        'percentage': (st.session_state.score / total_questions) * 100 if total_questions > 0 else 0,
        'incorrect_questions': st.session_state.incorrect_questions
    }

def reset_quiz():
    """Reset quiz state for a new attempt."""
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.answered_correctly = set()
    st.session_state.incorrect_questions = []
    st.session_state.practice_mode = False

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

def send_error_report(question_data: dict, user_report: str, contact_email: str = None):
    """Send error report via email using Gmail SMTP"""
    ADMIN_EMAIL = "remixonwin@gmail.com"
    
    # Format the error report
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_content = f"""
Error Report - Minnesota Driving Quiz
Time: {report_time}

Question Information:
-------------------
Question: {question_data['question']}
Current Answer: {question_data['correct_answer']}
Current Explanation: {question_data['explanation']}
Topic: {question_data['topic']}

User Report:
-----------
{user_report}

User Contact (optional):
----------------------
{contact_email if contact_email else 'Not provided'}
"""
    
    try:
        # Save to a local file as backup
        report_file = f"error_reports/report_{report_time.replace(':', '-')}.txt"
        os.makedirs("error_reports", exist_ok=True)
        with open(report_file, "w") as f:
            f.write(report_content)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = ADMIN_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"Quiz Error Report - {report_time}"
        msg.attach(MIMEText(report_content, 'plain'))
        
        return True, "Error report saved successfully! Thank you for helping improve the quiz."
    except Exception as e:
        return False, f"Could not save error report. Please try again later. Error: {str(e)}"