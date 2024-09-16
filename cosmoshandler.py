from gremlin_python.driver import client, serializer, protocol
from gremlin_python.driver.protocol import GremlinServerError
import sys
import os
import traceback
import pydanticmodels
from typing import Type
import json

# Set up vars for development
DATABASE_NAME = "mealdb"
GRAPH_NAME = "foods"
COSMOS_GREMLIN_ENDPOINT = os.environ["COSMOS_GREMLIN_ENDPOINT"]
COSMOS_GREMLIN_KEY = os.environ["COSMOS_GREMLIN_KEY"]

_gremlin_drop_operations = {
    "Drop Edge - Thomas no longer knows Mary": "g.V('thomas').outE('knows').where(inV().has('id', 'mary')).drop()",
    "Drop Vertex - Drop Thomas": "g.V('thomas').drop()"
}

def print_status_attributes(result):
    # This logs the status attributes returned for successful requests.
    # See list of available response status attributes (headers) that Gremlin API can return:
    #     https://docs.microsoft.com/en-us/azure/cosmos-db/gremlin-headers#headers
    #
    # These responses includes total request units charged and total server latency time.
    # 
    # IMPORTANT: Make sure to consume ALL results returend by cliient tothe final status attributes
    # for a request. Gremlin result are stream as a sequence of partial response messages
    # where the last response contents the complete status attributes set.
    #
    # This can be 
    print("\tResponse status_attributes:\n\t{0}".format(result.status_attributes))

def cleanup_graph(client):
    # This function clears all graph content
    _gremlin_cleanup_graph = "g.V().drop()"

    print("\n> {0}".format(
        _gremlin_cleanup_graph))
    callback = client.submitAsync(_gremlin_cleanup_graph)
    if callback.result() is not None:
        callback.result().all().result() 
    print("\n")
    print_status_attributes(callback.result())
    print("\n")


def insert_vertex(client, obj: Type[pydanticmodels.BaseModel]):
    """
    Inserts a vertex or vertices into the Graph database.

    Parameters:
    ----------
    obj : BaseModel
        The Pydantic object representing the vertex data.
    """
    
   # Get the label from the object dynamically using the type field
    label = getattr(obj, 'type', None)

    # Start with the basic addV query with the label
    query = f"g.addV('{label}')"
    
    # Iterate over the object's fields and add them as properties
    for field, value in obj.model_dump().items():
        if isinstance(value, str):
            query += f".property('{field}', '{value}')"
        # Handle non-string datatypes
        elif isinstance(value, (int, float, bool)):
            query += f".property('{field}', {value})"
        else:
            raise ValueError(f"Unsupported datatype for field {field}")
        
    callback = client.submitAsync(query)
    if callback.result() is not None:
        print("\tInserted this vertex:\n\t{0}".format(
            callback.result().all().result()))
    else:
        print("Something went wrong with this query: {0}".format(query))
    print("\n")
    print_status_attributes(callback.result())
    print("\n")

    print("\n")


def insert_edge(client, meal: str, ingredient:str, relation:str = 'contains'):

    # Construct query for adding edge
    query = f"g.V().hasId('{meal}').addE('{relation}').to(g.V('{ingredient}'))"

    # This function inserts edges
    callback = client.submitAsync(query)
    if callback.result() is not None:
            callback.result().all().result()
    else:
        print("Something went wrong with this query:\n\t{0}".format(query))
    print_status_attributes(callback.result())
    print("\n")

    print("\n")

def get_all_meals(client):
    # This function gets all available meals
    callback = client.submitAsync("g.V().where(outE('contains').inV().has('qty',gt(0)))")
    for result in callback.result():
        print(json.dumps(result, indent=4))

    print("/n")

def get_ingredients_for_meal(client, meal):
    # This function gets all ingredients for a meal and their location
    callback = client.submitAsync(f"g.V().hasId('{meal}').outE('contains').inV().valueMap(true,'location')")
    for result in callback.result():
        print(json.dumps(result, indent = 4))

    print("/n")


def execute_drop_operations(client):
    # This function drops vertices/edges
    for key in _gremlin_drop_operations:
        print("{0}:".format(key))
        print("\n> {0}".format(
            _gremlin_drop_operations[key]))
        callback = client.submitAsync(_gremlin_drop_operations[key])
        for result in callback.result():
            print(result)
        print_status_attributes(callback.result())
        print("\n")


try:
    client = client.Client(COSMOS_GREMLIN_ENDPOINT, 'g',
                           username=f"/dbs/{DATABASE_NAME}/colls/{GRAPH_NAME}",
                           password=COSMOS_GREMLIN_KEY,
                           message_serializer=serializer.GraphSONSerializersV2d0()
                           )

    print("Welcome to Azure Cosmos DB + Gremlin on Python!")

    # Drop the entire Graph
    input("We're about to drop whatever graph is on the server. Press any key to continue...")
    cleanup_graph(client)

    # Insert all vertices
    input("Let's insert some vertices into the graph. Press any key to continue...")
    thing = pydanticmodels.Ingredient(id = 'Cheese', location = 'Fridge', ingredientType = 'Fresh', qty = 1, type = 'ingredient')
    insert_vertex(client, thing)
    thing2 = pydanticmodels.Ingredient(id = 'Toast', location = 'Kitchen', ingredientType = 'Fresh', qty = 1, type = 'ingredient')
    insert_vertex(client, thing2)
    thing3 = pydanticmodels.Meal(id = 'Cheese on Toast', type = 'meal')
    insert_vertex(client, thing3)
    insert_edge(client, 'Cheese on Toast', 'Cheese')
    insert_edge(client, 'Cheese on Toast', 'Toast')

    # Find Cheese on Toast recipe
    input("Let's find the cheese on toast recipe. Press any key to continue...")
    get_all_meals(client)
    input("Let's get the ingredients for Cheese on Toast. Press any key to continue...")
    get_ingredients_for_meal(client, 'Cheese on Toast')

except GremlinServerError as e:
    print('Code: {0}, Attributes: {1}'.format(e.status_code, e.status_attributes))

    # GremlinServerError.status_code returns the Gremlin protocol status code
    # These are broad status codes which can cover various scenaios, so for more specific
    # error handling we recommend using GremlinServerError.status_attributes['x-ms-status-code']
    # 
    # Below shows how to capture the Cosmos DB specific status code and perform specific error handling.
    # See detailed set status codes than can be returned here: https://docs.microsoft.com/en-us/azure/cosmos-db/gremlin-headers#status-codes
    #
    # See also list of available response status attributes that Gremlin API can return:
    #     https://docs.microsoft.com/en-us/azure/cosmos-db/gremlin-headers#headers
    cosmos_status_code = e.status_attributes["x-ms-status-code"]
    if cosmos_status_code == 409:
        print('Conflict error!')
    elif cosmos_status_code == 412:
        print('Precondition error!')
    elif cosmos_status_code == 429:
        print('Throttling error!');
    elif cosmos_status_code == 1009:
        print('Request timeout error!')
    else:
        print("Default error handling")

    traceback.print_exc(file=sys.stdout)
    sys.exit(1)
 