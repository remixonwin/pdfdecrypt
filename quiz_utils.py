import streamlit as st
import random

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
    
    # Add Review Mistakes section with explanations
    if st.session_state.incorrect_questions:
        st.subheader("Review Incorrect Answers")
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
                
                # Add study tip based on topic
                st.info(f"📚 Study Tip: Review the section on {question['topic']} in the Minnesota Driver's Manual.")
    
    if st.button("Restart Quiz"):
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answered_correctly = set()
        st.session_state.incorrect_questions = []
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