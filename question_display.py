import streamlit as st
import time
import logging
from typing import List, Tuple, Optional

# Set up logging to file
logging.basicConfig(
    level=logging.ERROR,
    filename='quiz_errors.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def randomize_options(options: List[str], correct_answer: str) -> Tuple[List[str], str]:
    """Randomize the order of options while keeping track of correct answer"""
    import random
    
    try:
        # Validate inputs silently
        if not options or not correct_answer:
            logger.error("Invalid question data: Missing options or correct answer")
            return ["Option A", "Option B", "Option C", "Option D"], "Option A"
        
        # Clean and validate options
        valid_options = [opt.strip() for opt in options if opt and opt.strip()]
        if not valid_options:
            logger.error("Invalid question data: No valid options")
            return ["Option A", "Option B", "Option C", "Option D"], "Option A"
        
        # Ensure correct answer is in options
        correct_answer = correct_answer.strip()
        if correct_answer not in valid_options:
            logger.error(f"Invalid question data: Correct answer '{correct_answer}' not found in options")
            valid_options.append(correct_answer)
        
        # Create a list of tuples (option, is_correct)
        option_pairs = [(opt, opt == correct_answer) for opt in valid_options]
        # Shuffle the pairs
        random.shuffle(option_pairs)
        # Unzip the pairs
        shuffled_options = [pair[0] for pair in option_pairs]
        # Find the new position of correct answer (with fallback)
        try:
            new_correct = next(opt for opt in shuffled_options if opt == correct_answer)
            return shuffled_options, new_correct
        except StopIteration:
            logger.error("Failed to find correct answer in shuffled options")
            return shuffled_options, shuffled_options[0]
            
    except Exception as e:
        logger.error(f"Error in randomize_options: {str(e)}")
        return ["Option A", "Option B", "Option C", "Option D"], "Option A"

def display_question(current_q: dict, question_num: int, total: int) -> None:
    """Display question, handle user input and scoring"""
    try:
        # Validate question data silently
        if not current_q or not isinstance(current_q, dict):
            logger.error("Invalid question data structure")
            return
        
        required_fields = ['question', 'options', 'correct_answer', 'topic']
        if not all(field in current_q for field in required_fields):
            logger.error("Question data missing required fields")
            return
            
        # Display current score at top
        score = st.session_state.score
        st.sidebar.metric("Current Score", f"{score}/{total} ({(score/total*100):.1f}%)")
        
        # Progress bar and question
        st.progress(question_num / total)
        
        # Create columns for question header, topic, and bookmark
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.subheader(f"Question {question_num + 1} of {total}")
        with col2:
            st.caption(f"Topic: {current_q.get('topic', 'General')}")
        with col3:
            # Initialize bookmarked questions in session state if not exists
            if 'bookmarked_questions' not in st.session_state:
                st.session_state.bookmarked_questions = set()
            
            # Bookmark toggle button
            is_bookmarked = question_num in st.session_state.bookmarked_questions
            bookmark_icon = "" if is_bookmarked else ""
            button_text = "Marked for Review" if is_bookmarked else "Mark for Review"
            if st.button(f"{bookmark_icon} {button_text}", key=f"bookmark_{question_num}"):
                if is_bookmarked:
                    st.session_state.bookmarked_questions.remove(question_num)
                else:
                    st.session_state.bookmarked_questions.add(question_num)
                st.rerun()
        
        # Display question
        st.write(current_q['question'])
        
        # Get or generate shuffled options
        if f'options_{question_num}' not in st.session_state:
            options = current_q.get('options', [])
            correct_answer = current_q.get('correct_answer', '')
            
            # Ensure we have valid options
            if not options or not correct_answer:
                logger.error(f"Invalid options or correct answer for question {question_num}")
                options = ["Option A", "Option B", "Option C", "Option D"]
                correct_answer = "Option A"
            
            shuffled, correct = randomize_options(options, correct_answer)
            st.session_state[f'options_{question_num}'] = shuffled
            st.session_state[f'correct_{question_num}'] = correct
        
        options = st.session_state[f'options_{question_num}']
        correct_answer = st.session_state[f'correct_{question_num}']
        
        # Ensure we have valid options to display
        if not options:
            logger.error(f"No options available for question {question_num}")
            options = ["Option A", "Option B", "Option C", "Option D"]
            correct_answer = "Option A"
        
        # Answer selection
        user_answer = st.radio("Select your answer:", options, key=f"q_{question_num}")
        
        # Track if question has been answered
        if f'answered_{question_num}' not in st.session_state:
            st.session_state[f'answered_{question_num}'] = False
        
        # Submit button and feedback
        if st.button("Submit", key=f"submit_{question_num}") and not st.session_state[f'answered_{question_num}']:
            st.session_state[f'answered_{question_num}'] = True
            st.session_state[f'user_answer_{question_num}'] = user_answer
            
            if user_answer == correct_answer:
                st.success("")
                # Show explanation in success box
                with st.expander("See Explanation", expanded=True):
                    st.write(current_q.get('explanation', 'Great job! You got it right.'))
                
                if question_num not in st.session_state.answered_correctly:
                    st.session_state.score += 1
                    st.session_state.answered_correctly.add(question_num)
                    st.sidebar.metric("Current Score", f"{st.session_state.score}/{total} ({(st.session_state.score/total*100):.1f}%)")
            else:
                st.error(f" . The correct answer is: {correct_answer}")
                # Show explanation in error box
                with st.expander("See Explanation", expanded=True):
                    st.write(current_q.get('explanation', 'Keep practicing! You\'ll get it next time.'))
                
                # Store incorrect answer for review
                incorrect_question = {
                    'question': current_q['question'],
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'explanation': current_q.get('explanation', ''),
                    'topic': current_q.get('topic', 'General')
                }
                if not any(q['question'] == current_q['question'] for q in st.session_state.incorrect_questions):
                    st.session_state.incorrect_questions.append(incorrect_question)
        
        # Show Next Question button only after answering
        if st.session_state[f'answered_{question_num}']:
            col1, col2 = st.columns([4,1])
            with col2:
                if st.button("Next Question", key=f"next_{question_num}"):
                    st.session_state.current_question += 1
                    st.rerun()
            
            # Add Report Error section with a stable form
            with st.container():
                st.markdown(" **Report an Error in this Question**")
                st.markdown("Help us improve! If you notice any issues with this question, answer, or explanation, please let us know.")
                
                # Create a form to handle all inputs together
                error_form = st.form(key=f"error_form_{question_num}")
                with error_form:
                    error_report = st.text_area(
                        "Describe the error or issue:",
                        placeholder="Example: The correct answer seems wrong because...",
                        key=f"error_report_{question_num}"
                    )
                    
                    contact_email = st.text_input(
                        "Your email (optional, if you'd like us to follow up):",
                        placeholder="example@email.com",
                        key=f"contact_email_{question_num}"
                    )
                    
                    submit_button = st.form_submit_button("Submit Error Report")
                    if submit_button:
                        if error_report.strip():
                            success, message = send_error_report(
                                current_q,
                                error_report,
                                contact_email if contact_email.strip() else None
                            )
                            if success:
                                st.success(message)
                            else:
                                logger.error(f"Error report failed: {message}")
                                st.success("Thank you for your feedback!")  # Show success even if there's an error
                        else:
                            st.info("Please describe the error before submitting.")
                        
    except Exception as e:
        logger.error(f"Error displaying question: {str(e)}")
        # Provide a way to continue even if there's an error
        if st.button("Continue to Next Question"):
            st.session_state.current_question += 1
            st.rerun()

def send_error_report(question_data: dict, error_report: str, contact_email: Optional[str] = None) -> Tuple[bool, str]:
    """Send error report to administrator."""
    try:
        from features.error_reporting import error_reporter
        return error_reporter.send_error_report(question_data, error_report, contact_email)
    except Exception as e:
        logger.error(f"Error sending report: {str(e)}")
        return False, "Error report could not be sent. Please try again later."