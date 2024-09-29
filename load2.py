import csv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Set up MongoDB connection
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client['scholarship_db']
scholarships = db['scholarships']

def create_description(row):
    return f"Scholarship: {row['Scholarship Name']}\n" \
           f"Deadline: {row['Deadline']}\n" \
           f"Amount: {row['Amount']}\n" \
           f"Location: {row['Location']}\n" \
           f"Years: {row['Years']}\n" \
           f"Link: {row['Link']}\n" \
           f"Details: {row['Description']}"

def load_csv_to_mongodb(file_path):
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for index, row in enumerate(tqdm(reader, desc="Loading scholarships")):
            try:
                document = {
                    "id": index + 1,  # Start IDs from 1
                    "description": create_description(row)
                }

                # Insert into MongoDB
                scholarships.insert_one(document)
            except Exception as e:
                print(f"Error processing row: {row}")
                print(f"Error message: {str(e)}")

if __name__ == "__main__":
    csv_file_path = "load2.csv"  # Replace with your CSV file path
    load_csv_to_mongodb(csv_file_path)
    print("CSV data loaded into MongoDB successfully.")
