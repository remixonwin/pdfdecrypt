"""Script to remove duplicate questions from the quiz bank."""
from quiz_loader import remove_duplicates_from_csv

def main():
    print("Checking for duplicate questions...")
    success, message = remove_duplicates_from_csv()
    print(message)

if __name__ == "__main__":
    main()
