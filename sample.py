from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from pydanticmodels import Student
import sqlintegration

app = FastAPI()

# Dependency to get a database session
def get_db():
    db = sqlintegration.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fetch students from the database and return them using Pydantic models
@app.get("/students/", response_model=List[Student])
async def read_students(db: Session = Depends(get_db)):
    # Query the database using SQLAlchemy
    
    students = db.query(sqlintegration.Student).all()
    return students

# Insert students into the database
@app.post("/student", response_model=Student)
async def create_student(student: Student, db: Session = Depends(get_db)):
    # Generate insert query for DB
    student = sqlintegration.StudentSchema(firstname = student.firstname, lastname = student.lastname)
    db.add(student)
    try:
        db.commit()
        db.refresh()
    except Exception as e:
        print(f"Error adding student to the database: {e}")
    
    return student