# !pip install pymongo
import os
from pprint import pprint
from pymongo import MongoClient
from dotenv import load_dotenv

def get_database(): 
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
   client = MongoClient(MONGODB_URL)
 
   # Create the database for our example (we will use the same database throughout the tutorial
   return client['Sensors_Connect_DB_V2']
  

# Load environment variables from .env file
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
db= get_database()



# Given location coordinates
def get_nearByPlaces(latitude, longitude, collection_name, search_range= 5000, limit=3):
    collection=db[collection_name]
    given_location = {
        "type": "Point",
        "coordinates": [longitude, latitude]  # Replace with the actual coordinates of the given location
    }

    # Maximum distance in meters
    max_distance_in_meters = search_range  # Replace with your desired maximum distance

    # Query to find documents near the given location
    query = {
        "location": {
            "$nearSphere": {
                "$geometry": given_location,
                "$maxDistance": max_distance_in_meters
            }
        }
    }

    # Execute the query
    result = collection.find(query).limit(limit)
    return result
