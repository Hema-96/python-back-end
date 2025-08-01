connection_url = "postgresql://postgres.poptklbkuamytrzcgeiy:8gWkOCJOugd6Idj5@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str
    name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
from sqlmodel import create_engine, Session
engine = create_engine(connection_url, echo=True)

from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    # Cleanup if needed 
    
app = FastAPI(lifespan=lifespan)

@app.post("/users/")    
def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

from typing import List 
from sqlmodel import select

@app.get("/users/", response_model=List[User])
def read_users():
    with Session(engine) as session:
        statement = select(User)
        results = session.exec(statement).all()
    return results

