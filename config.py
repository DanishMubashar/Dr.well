# config.py
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Dr. Well - AI Medical Assistant"
APP_ICON = "🤖"
APP_VERSION = "3.0.0"

# Google API Key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyD7qx_7VnCk3IxDqLAxiAZDz2H0E7jE9VY')

MEDICAL_SPECIALTIES = [
    "Cardiologist", "Dermatologist", "Neurologist", "Orthopedic Surgeon",
    "Pediatrician", "Psychiatrist", "Ophthalmologist", "ENT Specialist",
    "Gynecologist", "General Physician", "Dentist", "Physiotherapist"
]

# Food restrictions for different conditions
FOOD_RESTRICTIONS = {
    "diabetes": ["Avoid: Sugar, White rice, White bread, Soda, Sweet fruits"],
    "high blood pressure": ["Avoid: Salt, Processed food, Pickles, Canned food, Fast food"],
    "heart disease": ["Avoid: Fried food, Red meat, Butter, Cheese, Coconut oil"],
    "kidney disease": ["Avoid: Salt, Bananas, Oranges, Potatoes, Tomatoes"],
    "gastric": ["Avoid: Spicy food, Oily food, Caffeine, Carbonated drinks"],
    "fever": ["Avoid: Oily food, Spicy food, Dairy products"],
    "cold": ["Avoid: Cold drinks, Ice cream, Dairy, Fried food"],
    "allergy": ["Avoid: Foods causing allergy, Processed food, Artificial colors"]
}
