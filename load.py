import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv('MONGO_URI')


# Connect to MongoDB
client = MongoClient(URI, server_api=ServerApi('1'))
db = client['scholarship_db']
scholarships = db['scholarships']

# Load JSON data from file
with open('scrape.json', 'r') as file:
    scholarship_data = json.load(file)

# Insert scholarships into MongoDB
for scholarship in scholarship_data:
    # Insert the scholarship
    result = scholarships.insert_one(scholarship)
    print(f"Inserted scholarship with ID: {result.inserted_id}")

print(f"Total scholarships inserted: {len(scholarship_data)}")

# Close the MongoDB connection
client.close()
