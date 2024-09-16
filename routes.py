from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from typing import List

from pydanticmodels import Food

router = APIRouter()

@router.get("/listall", response_description="List of all foods", response_model=List[Food])
async def list_foods(request: Request):
    foods = [food async for food in request.app.state.food_container.read_all_items()]
    return foods

# @router.put("/update", response_model = Food)
# async def replace_food(request: Request, item_with_update:Food):
#     # Make sure the partition key is correctly set (adjust if necessary)
#     partition_key = item_with_update.location
    
#     # Read the existing item from Cosmos DB
#     existing_item = await request.app.state.food_container.read_item(
#         item_with_update.location, partition_key=partition_key
#     )
#     # Convert existing item and update data to dictionaries
#     existing_item_dict = jsonable_encoder(existing_item)
#     update_dict = jsonable_encoder(item_with_update)

#     # Merge updates into existing item
#     for key, value in update_dict.items():
#         if value is not None:  # Only update non-null values
#             existing_item_dict[key] = value

#     for (k) in update_dict.keys():
#         if update_dict[k]:
#             existing_item_dict[k] = update_dict[k]
#     # Replace the item in Cosmos DB
#     updated_item = await request.app.state.food_container.replace_item(
#         item_with_update.id, existing_item_dict
#     )
#     return updated_item

@router.post("/insert", response_model=Food)
async def create_food(request: Request, food_item: Food):
    food_item = jsonable_encoder(food_item)
    new_food = await request.app.state.food_container.create_item(food_item, enable_automatic_id_generation=True)
    return new_food

# @router.delete("/delete")
# async def delete_food(request: Request, item_id: str, partition_key: str):
#     # try:
#         # Read the existing item from Cosmos DB
#         existing_item = await request.app.state.food_container.read_item(
#             item_id, partition_key=partition_key
#         )
        
#         # Log existing item for debugging
#         logger.debug("Existing item: %s", existing_item)
        
#         # Delete the item from Cosmos DB
#         await request.app.state.food_container.delete_item(
#             item_id, partition_key=partition_key
#         )
        
#         return {"message": "Item deleted successfully"}