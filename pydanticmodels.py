from pydantic import BaseModel, ValidationError
from enum import Enum
from typing import Literal

class IngredientTypes(str, Enum):
    # Types for ingredients
    Fresh = 'Fresh'
    Frozen = 'Frozen'
    Chilled = 'Chilled'
    
class Ingredient(BaseModel):
    # Ingredient class
    name : str # name of the food
    location: str # location i.e. garage, house etc.
    type: Literal['ingredient']
    ingredientType: IngredientTypes

class MealCategory(BaseModel):
    # Meal class
    name: str # name of the meal
    type: Literal['meal']