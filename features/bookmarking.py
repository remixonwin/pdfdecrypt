"""Bookmarking functionality for the quiz application."""
from typing import Set, List, Dict, Any
import streamlit as st

class BookmarkManager:
    """Manages bookmarked questions and related functionality."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize bookmark-related session state variables."""
        if 'bookmarked_questions' not in st.session_state:
            st.session_state.bookmarked_questions = set()
    
    @staticmethod
    def toggle_bookmark(question_num: int) -> bool:
        """Toggle bookmark status for a question."""
        BookmarkManager.initialize_session_state()
        
        if question_num in st.session_state.bookmarked_questions:
            st.session_state.bookmarked_questions.remove(question_num)
            return False
        else:
            st.session_state.bookmarked_questions.add(question_num)
            return True
    
    @staticmethod
    def is_bookmarked(question_num: int) -> bool:
        """Check if a question is bookmarked."""
        BookmarkManager.initialize_session_state()
        return question_num in st.session_state.bookmarked_questions
    
    @staticmethod
    def get_bookmarked_questions() -> Set[int]:
        """Get set of bookmarked question numbers."""
        BookmarkManager.initialize_session_state()
        return st.session_state.bookmarked_questions
    
    @staticmethod
    def create_practice_session(questions: List[Dict[str, Any]]):
        """Create a practice session from bookmarked questions."""
        BookmarkManager.initialize_session_state()
        
        if st.session_state.bookmarked_questions:
            st.session_state.practice_mode = True
            st.session_state.practice_questions = [
                questions[q_num] for q_num in st.session_state.bookmarked_questions
            ]
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answered_correctly = set()
            st.session_state.incorrect_questions = []
            return True
        return False

# Create global bookmark manager instance
bookmark_manager = BookmarkManager()
