from fastapi import FastAPI
from app.crud import create_user, get_users
from app.models import User


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Firebase API is live!"}

@app.get("/users")
def get_all_users():
    return get_users()

@app.post("/users")
def add_user(user: User):
    return create_user(user)
