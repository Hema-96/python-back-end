from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_active: Optional[bool] = True
