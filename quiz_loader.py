import csv
from pathlib import Path
import streamlit as st
from typing import List

# Define the path to your CSV file
csv_file_path = 'Minnesota_Driving_Quiz.csv'

# Read the CSV file and clean the options
cleaned_rows = []
with open(csv_file_path, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Filter out None keys
        row = {k: v for k, v in row.items() if k is not None}
        # Clean the options by removing "a) ", "b) ", "c) ", "d) " prefixes
        row['Option A'] = row['Option A'].replace('a) ', '').strip()
        row['Option B'] = row['Option B'].replace('b) ', '').strip()
        row['Option C'] = row['Option C'].replace('c) ', '').strip()
        row['Option D'] = row['Option D'].replace('d) ', '').strip()
        cleaned_rows.append(row)

# Write the cleaned rows back to the same CSV file
with open(csv_file_path, 'w', newline='') as file:
    fieldnames = ['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cleaned_rows)

print(f"Options cleaned and saved to {csv_file_path}.")

@st.cache_data
def load_quiz_data() -> List[dict]:
    """Load quiz data from CSV and convert to proper format"""
    quiz_data = []
    csv_path = Path("Minnesota_Driving_Quiz.csv")
    
    try:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Format question data
                    question = {
                        'question': row['Question'],
                        'options': [row['Option A'], row['Option B'], row['Option C'], row['Option D']],
                        'correct_answer': row['Correct Answer']
                    }
                    # Ensure options are properly formatted
                    question['options'] = [opt.strip() if opt is not None else '' for opt in question['options']]
                    # Ensure correct answer is properly formatted
                    question['correct_answer'] = question['correct_answer'].strip() if question['correct_answer'] is not None else ''
                    quiz_data.append(question)
                except KeyError as e:
                    st.error(f"Missing or incorrect key in CSV data: {str(e)}")
    except Exception as e:
        st.error(f"Error reading quiz data: {str(e)}")
    
    return quiz_data