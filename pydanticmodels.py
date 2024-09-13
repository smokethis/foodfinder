from pydantic import BaseModel

# Pydantic model for the response
class Student(BaseModel):
    id: int = None
    firstname: str
    lastname: str

    class Config:
        from_attributes = True  # Enable compatibility with ORM models like SQLAlchemy
