from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from openai import OpenAI
from tqdm import tqdm
from pydantic import BaseModel, Field
from typing import Optional

# Load environment variables
load_dotenv()

# Set up MongoDB connection
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client['scholarship_db']
scholarships = db['scholarships']

# Set up OpenAI API
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# Define the structured output model
class AugmentedScholarship(BaseModel):
    title: str
    is_merit_based: bool
    preferred_ethnicity: Optional[str] = Field(None, description="Preferred ethnicity, if any")
    preferred_gender: Optional[str] = Field(None, description="Preferred gender, if any")
    preferred_major: Optional[str] = Field(None, description="Preferred major or field of study, if any")
    prefers_lgbt: bool
    university: Optional[str] = Field(None, description="Specific university, if any")
    location: Optional[str] = Field(None, description="Location requirement, if any")
    is_essay_required: bool
    reward: float = Field(description="Scholarship amount in USD")
    extra_requirements: Optional[str] = Field(None, description="Any additional requirements")
    women_in_stem: bool
    disabilities: bool
    rural: bool
    immigrant_or_refugee: bool
    neurodiversity: bool
    low_income: bool
    first_generation: bool

def augment_document(doc):
    if "name" in doc:
        return doc

    prompt = f"""
    Given the following scholarship description, please extract or infer the required information:

    Description: {doc['description']}

    Provide the information in a structured format following the specified schema.
    If a field is not applicable or the information is not provided, use null for optional fields.
    """

    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",  # Use the appropriate model that supports structured outputs
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts scholarship information."},
            {"role": "user", "content": prompt}
        ],
        response_format=AugmentedScholarship
    )

    result = response.choices[0].message
    parsed = result.parsed

    # Merge the augmented data with the original document
    doc.update(parsed)
    return doc


# Main execution
if __name__ == "__main__":
    # Get all documents from the collection
    all_docs = list(scholarships.find())

    # Process each document
    for doc in tqdm(all_docs, desc="Processing scholarships"):
        try:
            augmented_doc = augment_document(doc)

            # Update the document in the database
            scholarships.update_one({"_id": doc["_id"]}, {"$set": augmented_doc})
        except Exception as e:
            print(f"Error processing document {doc['_id']}: {str(e)}")

    print(f"Processed and updated {len(all_docs)} scholarships.")

    # Close the MongoDB connection
    client.close()
