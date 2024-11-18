"""Main Streamlit application for Minnesota Driver's Quiz."""
import streamlit as st
from quiz_utils import (
    initialize_quiz_state,
    get_current_question,
    load_user_progress,
    reset_quiz
)
from question_display import display_question

def main():
    # Set page config
    st.set_page_config(
        page_title="Minnesota Driver's License Quiz",
        page_icon="🚗",
        layout="wide"
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 10px 24px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .reportform {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Main title with emoji
    st.title("🚗 Minnesota Driver's License Quiz")
    
    # Initialize quiz state
    initialize_quiz_state()
    
    # Load progress
    progress = load_user_progress()
    total_questions = len(st.session_state.questions) if hasattr(st.session_state, 'questions') else 0
    
    # Safety check for total_questions
    if total_questions == 0:
        st.error("No questions loaded. Please check the quiz data.")
        if st.button("Retry Loading Questions"):
            st.session_state.clear()
            st.rerun()
        return
        
    # Initialize current_question if not present
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    answered_correctly = len(progress['correct_questions']) if progress else 0
    
    # Create a container for metrics
    with st.container():
        # Display progress metrics in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Score", f"{st.session_state.score}/{total_questions}")
        with col2:
            st.metric("Questions Mastered", f"{answered_correctly}/{total_questions}")
        with col3:
            remaining = total_questions - answered_correctly
            st.metric("Questions Remaining", str(remaining))
        
        # Display progress bar with safety checks
        progress_percentage = min((st.session_state.current_question / total_questions) * 100, 100) if total_questions > 0 else 0
        st.progress(progress_percentage / 100)
    
    # Create main content container
    main_container = st.container()
    
    with main_container:
        # Get and display current question
        current_question = get_current_question()
        if current_question:
            display_question(current_question, st.session_state.current_question, total_questions)
        else:
            # Quiz completion screen
            st.success("🎉 Congratulations! You've completed the quiz!")
            st.balloons()
            
            # Show final score and stats
            final_score = st.session_state.score
            score_percentage = (final_score / total_questions) * 100
            
            st.markdown(f"""
                ### Final Results
                - **Score**: {final_score}/{total_questions}
                - **Percentage**: {score_percentage:.1f}%
                - **Questions Mastered**: {answered_correctly}/{total_questions}
            """)
            
            # Add encouraging message based on score
            if score_percentage >= 80:
                st.success("🌟 Excellent work! You're well prepared for your driver's license test!")
            elif score_percentage >= 70:
                st.info("👍 Good job! With a bit more practice, you'll be fully prepared!")
            else:
                st.warning("📚 Keep practicing! Review the questions you missed and try again.")
            
            # Restart quiz button
            if st.button("Start New Quiz", use_container_width=True):
                reset_quiz()
                st.rerun()
    
    # Add footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
        <p>Made with ❤️ for Minnesota Drivers</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
