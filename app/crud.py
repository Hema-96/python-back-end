from app.firebase_config import db
from app.models import User

def get_users(user: User):
    users_ref = db.collection("users")
    docs = users_ref.stream()
    return [doc.to_dict() for doc in docs]

def create_user(user: User):
    doc_ref = db.collection("users").document()  # Auto ID
    doc_ref.set(user.dict())
    return {"message": "User added", "id": doc_ref.id}