import csv
from collections import Counter

# Define the path to your CSV file
csv_file_path = 'Minnesota_Driving_Quiz.csv'

# Read the CSV file and collect questions
questions = []
rows = []
with open(csv_file_path, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Filter out None keys
        row = {k: v for k, v in row.items() if k is not None}
        # Remove double quotes from questions and options
        row = {k: v.replace('"', '') if isinstance(v, str) else v for k, v in row.items()}
        questions.append(row['Question'])
        rows.append(row)

# Count the occurrences of each question
question_counts = Counter(questions)

# Identify duplicate questions
duplicates = {question: count for question, count in question_counts.items() if count > 1}

if duplicates:
    print("Duplicate questions found and will be removed:")
    for question, count in duplicates.items():
        print(f"{question} (appears {count} times)")
else:
    print("No duplicate questions found.")

# Remove duplicates, keeping the first occurrence
seen_questions = set()
unique_rows = []
for row in rows:
    question = row['Question']
    if question not in seen_questions:
        unique_rows.append(row)
        seen_questions.add(question)

# Ensure all rows have the same keys
fieldnames = unique_rows[0].keys()
for row in unique_rows:
    if row.keys() != fieldnames:
        print(f"Row with mismatched keys: {row.keys()}")
        raise ValueError("Row contains fields not in fieldnames")

# Write the unique rows back to the same CSV file
with open(csv_file_path, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(unique_rows)

print(f"Duplicates removed. Unique questions saved to {csv_file_path}.")