"""
MongoDB initialization script for Meal-Sharing Web Application
Initializes collections and inserts sample data
"""

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def init_mongodb():
    """Initialize MongoDB database with sample data"""
    
    # Connect to MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(MONGO_URI)
    
    # Create/get database
    db = client['campus_meal_plan']
    
    # Clear existing data (for fresh start)
    db.favorites.delete_many({})
    db.reviews.delete_many({})
    
    # Insert sample favorites
    favorites_data = [
        {
            'user_id': 'U001',
            'recipe_id': 101,
            'saved_at': datetime.utcnow(),
            'notes': 'Loved this for meal prep!'
        },
        {
            'user_id': 'U002',
            'recipe_id': 203,
            'saved_at': datetime.utcnow(),
            'notes': 'Try with extra sauce next time.'
        },
        {
            'user_id': 'U001',
            'recipe_id': 3,
            'saved_at': datetime.utcnow(),
            'notes': 'Great for quick dinners'
        },
        {
            'user_id': 'U003',
            'recipe_id': 2,
            'saved_at': datetime.utcnow(),
            'notes': 'Healthy and delicious'
        }
    ]
    
    db.favorites.insert_many(favorites_data)
    print(f"Inserted {len(favorites_data)} favorites into MongoDB")
    
    # Insert sample reviews
    reviews_data = [
        {
            'recipe_id': 101,
            'user_id': 'U001',
            'rating': 5,
            'comment': 'Loved this meal! Perfect balance of flavor and nutrition.',
            'created_at': datetime(2025, 10, 18, 21, 15, 0)
        },
        {
            'recipe_id': 203,
            'user_id': 'U002',
            'rating': 4,
            'comment': 'Pretty good, but portion size could be bigger.',
            'created_at': datetime(2025, 10, 18, 21, 20, 0)
        },
        {
            'recipe_id': 107,
            'user_id': 'U003',
            'rating': 3,
            'comment': 'It was okay — would add more spice next time.',
            'created_at': datetime(2025, 10, 18, 21, 25, 0)
        },
        {
            'recipe_id': 1,
            'user_id': 'U001',
            'rating': 5,
            'comment': 'Best chicken stir fry recipe ever!',
            'created_at': datetime.utcnow()
        },
        {
            'recipe_id': 2,
            'user_id': 'U002',
            'rating': 5,
            'comment': 'Love this buddha bowl! So healthy and filling.',
            'created_at': datetime.utcnow()
        }
    ]
    
    db.reviews.insert_many(reviews_data)
    print(f"Inserted {len(reviews_data)} reviews into MongoDB")
    
    # Create indexes for better performance
    db.favorites.create_index('user_id')
    db.favorites.create_index('recipe_id')
    db.reviews.create_index('recipe_id')
    db.reviews.create_index('user_id')
    
    print("MongoDB initialization complete!")
    print(f"Database: campus_meal_plan")
    print(f"Collections: favorites, reviews")
    
    client.close()

if __name__ == "__main__":
    init_mongodb()
