from fastapi import FastAPI
from azure.cosmos import PartitionKey, exceptions
from routes import router as food_router
from contextlib import asynccontextmanager
from gremlin_python.driver import client, serializer
import os

# Set up vars for development
DATABASE_NAME = "mealdb"
GRAPH_NAME = "meals"
COSMOS_GREMLIN_ENDPOINT = os.environ["COSMOS_GREMLIN_ENDPOINT"]
COSMOS_GREMLIN_KEY = os.environ["COSMOS_GREMLIN_KEY"]

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Define Cosmos connection
#         app.state.cosmos_client = client.Client(
#         url=COSMOS_GREMLIN_ENDPOINT,
#         traversal_source="g",
#         username=f"/dbs/{DATABASE_NAME}/colls/{GRAPH_NAME}",
#         password=COSMOS_GREMLIN_KEY,
#         message_serializer=serializer.GraphSONSerializersV2d0(),
#     )
#     # Configure Database Connection
#     await 
#     yield
#     # Clean up any resources if needed (e.g., closing connections)
#     app.state.cosmos_client.submitAsync("g.V().drop()")

# Start FastAPI app
# app = FastAPI(lifespan=lifespan)
app = FastAPI()
# Include the external router definition(s)
app.include_router(food_router, tags=["foods"], prefix="/foods")

# async def connect_to_db(db_name):
#     try:
#         app.state.database  = app.state.cosmos_client.get_database_client(db_name)
#     except exceptions.CosmosResourceNotFoundError as e:
#         print(f"Database not found: {e}")
#         raise

# async def connect_to_container(container_name):
#     try:
#         # Can't seem to change the food_container definition dynamically which is a bit pants
#         app.state.food_container = app.state.database.get_container_client(container_name)
#     except exceptions.CosmosHttpResponseError:
#         raise