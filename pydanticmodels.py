from pydantic import BaseModel, ValidationError
from typing import Literal

class Ingredient(BaseModel):
    # Ingredient class
    id : str # name of the food
    location: str # location i.e. garage, house etc.
    type: Literal['ingredient']
    qty: int
    ingredientType: Literal['Fresh','Frozen','Chilled']

class Meal(BaseModel):
    # Meal class
    id: str # name of the meal
    type: Literal['meal']