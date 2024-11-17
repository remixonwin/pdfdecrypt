import csv

# Define the path to your CSV file
csv_file_path = 'Minnesota_Driving_Quiz.csv'

# Read the CSV file and clean the options and correct answers
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
        
        # Ensure the correct answer is in the correct format
        correct_answer = row.get('Correct Answer')
        if correct_answer:
            correct_answer = correct_answer.strip()
            if correct_answer.startswith('a) '):
                row['Correct Answer'] = row['Option A']
            elif correct_answer.startswith('b) '):
                row['Correct Answer'] = row['Option B']
            elif correct_answer.startswith('c) '):
                row['Correct Answer'] = row['Option C']
            elif correct_answer.startswith('d) '):
                row['Correct Answer'] = row['Option D']
            else:
                # If the correct answer does not match any option, log an error
                print(f"Error: Correct answer '{correct_answer}' does not match any option for question: {row['Question']}")
        else:
            print(f"Error: Correct answer is missing for question: {row['Question']}")
        
        cleaned_rows.append(row)

# Write the cleaned rows back to the same CSV file
with open(csv_file_path, 'w', newline='') as file:
    fieldnames = ['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cleaned_rows)

print(f"Options and correct answers cleaned and saved to {csv_file_path}.")