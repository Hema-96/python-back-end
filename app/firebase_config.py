import os
import firebase_admin
from firebase_admin import credentials, firestore

# Check if running on Render
firebase_json_path = (
    "/etc/secrets/firebase-adminsdk.json"
    if os.getenv("RENDER") == "true"
    else "C:/wamp64/www/python-backend/python-back-end/firebase-adminsdk.json"
)

# Initialize Firebase
cred = credentials.Certificate(firebase_json_path)
firebase_admin.initialize_app(cred)

# ✅ Create Firestore client (required for import)
db = firestore.client()
