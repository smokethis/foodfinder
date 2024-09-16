from gremlin_python.driver import client, serializer, protocol
from gremlin_python.driver.protocol import GremlinServerError
import sys
import os
import traceback
import pydanticmodels
from typing import Type

# Set up vars for development
DATABASE_NAME = "mealdb"
GRAPH_NAME = "foods"
COSMOS_GREMLIN_ENDPOINT = os.environ["COSMOS_GREMLIN_ENDPOINT"]
COSMOS_GREMLIN_KEY = os.environ["COSMOS_GREMLIN_KEY"]

_gremlin_insert_edges = [
    "g.V('thomas').addE('knows').to(g.V('mary'))",
    "g.V('thomas').addE('knows').to(g.V('ben'))",
    "g.V('ben').addE('knows').to(g.V('robin'))"
]

_gremlin_update_vertices = [
    "g.V('thomas').property('age', 45)"
]

_gremlin_count_vertices = "g.V().count()"

_gremlin_traversals = {
    "Get all persons older than 40": "g.V().hasLabel('person').has('age', gt(40)).values('firstName', 'age')",
    "Get all persons and their first name": "g.V().hasLabel('person').values('firstName')",
    "Get all persons sorted by first name": "g.V().hasLabel('person').order().by('firstName', incr).values('firstName')",
    "Get all persons that Thomas knows": "g.V('thomas').out('knows').hasLabel('person').values('firstName')",
    "People known by those who Thomas knows": "g.V('thomas').out('knows').hasLabel('person').out('knows').hasLabel('person').values('firstName')",
    "Get the path from Thomas to Robin": "g.V('thomas').repeat(out()).until(has('id', 'robin')).path().by('firstName')"
}

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


def insert_vertex(client, obj: Type[pydanticmodels.BaseModel], label_field: str):
    """
    Inserts a vertex or vertices into the Graph database.

    Parameters:
    ----------
    obj : BaseModel
        The Pydantic object representing the vertex data.
    label_field : str
        The name of the field to be used as the vertex label.
    """
    
    # Get the label from the pydantic object
    label = label_field

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

    print("\n> {0}\n".format(query))
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


def insert_edges(client):
    # This function inserts edges
    for query in _gremlin_insert_edges:
        print("\n> {0}\n".format(query))
        callback = client.submitAsync(query)
        if callback.result() is not None:
            print("\tInserted this edge:\n\t{0}\n".format(
                callback.result().all().result()))
        else:
            print("Something went wrong with this query:\n\t{0}".format(query))
        print_status_attributes(callback.result())
        print("\n")

    print("\n")


def update_vertices(client):
    # This function updates vertices
    for query in _gremlin_update_vertices:
        print("\n> {0}\n".format(query))
        callback = client.submitAsync(query)
        if callback.result() is not None:
            print("\tUpdated this vertex:\n\t{0}\n".format(
                callback.result().all().result()))
        else:
            print("Something went wrong with this query:\n\t{0}".format(query))

        print_status_attributes(callback.result())
        print("\n")

    print("\n")


def count_vertices(client):
    # This function counts vertices
    print("\n> {0}".format(
        _gremlin_count_vertices))
    callback = client.submitAsync(_gremlin_count_vertices)
    if callback.result() is not None:
        print("\tCount of vertices: {0}".format(callback.result().all().result()))
    else:
        print("Something went wrong with this query: {0}".format(
            _gremlin_count_vertices))

    print("\n")
    print_status_attributes(callback.result())
    print("\n")


def execute_traversals(client):
    # This function traverses vertices
    for key in _gremlin_traversals:
        print("{0}:".format(key))
        print("> {0}\n".format(
            _gremlin_traversals[key]))
        callback = client.submitAsync(_gremlin_traversals[key])
        for result in callback.result():
            print("\t{0}".format(str(result)))
        
        print("\n")
        print_status_attributes(callback.result())
        print("\n")


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
    thing = pydanticmodels.Ingredient(name = 'Cheese', location = 'Fridge', ingredientType = 'Fresh', type = 'ingredient')
    insert_vertex(client, thing, 'Food')

    

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

print("\nAnd that's all! Sample complete")
input("Press Enter to continue...")