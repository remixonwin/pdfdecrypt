"""Question display and interaction handling."""
import streamlit as st
import random
import logging
from typing import List, Tuple, Optional

# Set up logging to file
logging.basicConfig(
    level=logging.ERROR,
    filename='quiz_errors.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_question_options(current_q: dict, question_num: int) -> Tuple[List[str], str]:
    """Get or create randomized options for a question."""
    options_key = f"options_{question_num}"
    correct_key = f"correct_{question_num}"
    
    # If options are already stored in session state, use them
    if options_key in st.session_state and correct_key in st.session_state:
        return st.session_state[options_key], st.session_state[correct_key]
    
    # Otherwise, create new randomized options
    try:
        options = current_q['options']
        correct_answer = current_q['correct_answer']
        
        # Validate inputs
        if not options or not correct_answer:
            logger.error("Invalid question data: Missing options or correct answer")
            default_options = ["Option A", "Option B", "Option C", "Option D"]
            st.session_state[options_key] = default_options
            st.session_state[correct_key] = "Option A"
            return default_options, "Option A"
        
        # Clean and validate options
        valid_options = [opt.strip() for opt in options if opt and opt.strip()]
        if not valid_options:
            logger.error("Invalid question data: No valid options")
            default_options = ["Option A", "Option B", "Option C", "Option D"]
            st.session_state[options_key] = default_options
            st.session_state[correct_key] = "Option A"
            return default_options, "Option A"
        
        # Ensure correct answer is in options
        correct_answer = correct_answer.strip()
        if correct_answer not in valid_options:
            valid_options.append(correct_answer)
        
        # Shuffle options
        random.shuffle(valid_options)
        
        # Store in session state
        st.session_state[options_key] = valid_options
        st.session_state[correct_key] = correct_answer
        
        return valid_options, correct_answer
            
    except Exception as e:
        logger.error(f"Error in get_question_options: {str(e)}")
        default_options = ["Option A", "Option B", "Option C", "Option D"]
        st.session_state[options_key] = default_options
        st.session_state[correct_key] = "Option A"
        return default_options, "Option A"

def display_question(current_q: dict, question_num: int, total: int):
    """Display question and handle user interaction."""
    try:
        # Create container for question content
        question_container = st.container()
        
        with question_container:
            # Question header
            st.write(f"### Question {question_num + 1} of {total}")
            
            # Question text
            st.markdown(f"**{current_q['question']}**")
            
            # Get options (will be consistent due to session state)
            options, correct_answer = get_question_options(current_q, question_num)
            
            # Create unique keys for this question
            answer_key = f"answer_{question_num}"
            check_key = f"check_{question_num}"
            answered_key = f"answered_{question_num}"
            
            # Only show options if question hasn't been answered
            if not st.session_state.get(answered_key, False):
                # Create columns for better layout
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    user_answer = st.radio("Select your answer:", options, key=answer_key)
                
                with col2:
                    # Center the check answer button
                    st.write("")  # Add some spacing
                    if st.button("Check Answer", key=check_key, use_container_width=True):
                        st.session_state[answered_key] = True
                        
                        # Process answer
                        is_correct = user_answer == current_q['correct_answer']
                        
                        if is_correct:
                            st.success("✅ Correct!")
                            st.session_state.score += 1
                        else:
                            st.error("❌ Incorrect!")
                            st.warning(f"The correct answer is: {correct_answer}")
                            
                            # Show explanation if available
                            if current_q.get('explanation'):
                                with st.expander("See Explanation"):
                                    st.info(current_q['explanation'])
                        
                        # Show next question button
                        if st.button("Next Question", use_container_width=True):
                            st.session_state.current_question += 1
                            st.rerun()
            else:
                # Show the selected answer and feedback when question is answered
                st.info(f"Your answer: {st.session_state[answer_key]}")
                if st.session_state.get(f"correct_{question_num}", False):
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Incorrect!")
                    st.warning(f"The correct answer is: {correct_answer}")
                    if current_q.get('explanation'):
                        with st.expander("See Explanation"):
                            st.info(current_q['explanation'])
                
                # Show next question button
                if st.button("Next Question", use_container_width=True):
                    st.session_state.current_question += 1
                    st.rerun()
            
            # Show report error button
            with st.expander("Report an Issue"):
                error_report = st.text_area("Describe the issue:", key=f"report_{question_num}")
                contact_email = st.text_input("Your email (optional):", key=f"email_{question_num}")
                
                if st.button("Submit Report", key=f"submit_report_{question_num}"):
                    try:
                        with open('error_reports.log', 'a') as f:
                            f.write(f"\n{'='*50}\nQuestion: {current_q['question']}\nReport: {error_report}\nEmail: {contact_email}\n")
                        st.success("Thank you for your feedback!")
                    except Exception as e:
                        st.error("Failed to submit report. Please try again.")
                        logger.error(f"Error saving report: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error displaying question: {str(e)}")
        st.error("An error occurred while displaying the question. Please try again.")