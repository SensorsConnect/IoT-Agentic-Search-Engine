import ssl

import logging
from colorlog import ColoredFormatter
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from graph import runnable

app = FastAPI()
#  This part achive secure connection to your server need to be done latw
# https://medium.com/@mariovanrooij/adding-https-to-fastapi-ad5e0f9e084e#:~:text=To%20use%20HTTPS%2C%20simply%20change,.com%2Fapi%2Fendpoint%20.
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain('cert.pem', keyfile='key.pem')
origins = ["*"]
# for security purpose, you might need to define certain IPs that can request a service
# origins = ["http://localhost",
#     "http://localhost:37889"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the logging module
# Configure the logging settings
logging.getLogger().handlers = []  # Remove any existing handlers
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(log_color)s%(levelname)-8s%(reset)s %(message)s'))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)
#turn off debugger
# logging.disable()
# class Item(BaseModel):
#     title: str
#     price: float
#     is_offer: Union[bool, None] = None

class Item(BaseModel):
    title: str
    id: int
    userId:int

class Query(BaseModel):
    text:str


@app.get("/")
def read_root():
    return {"title": "World",  "userId": 1, "id": 1}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    print(item.title)
    return item
    return {"item_name": item.title, "item_id": item_id}

@app.put("/query")
def query_handler(query: Query):
    print(query.text)
    thread = {"configurable": {"thread_id": "a"}}


    human_message = HumanMessage(content=query.text)
    messages = [human_message]

    result = runnable.invoke({"messages":messages}, thread)

    return  {"answer": result["response"]}
    return {"item_name": item.title, "item_id": item_id}



def printResults(results):
    services_name_addresses=[]
    for result in results:
        logging.info(result['Service Address'])
        logging.info(result['Service Name'])
        logging.info(result['location']['coordinates'])
        services_name_addresses.append([result['Service Name'],result['Service Address']])
    return services_name_addresses


# while True:
        
#     user_query = input("Enter your query: ")
#     refined_user_query=user_query
#     # refined_user_query = query_refining_func(query=user_query)

#     # query_type = query_type_func(query=refined_user_query)
#     services_types, entities, addresses = query_understanding_engine(
#         query=refined_user_query)

#     # print("Query type: " + query_type)
#     print("Services types (top 3 in semantic meaning): " + str(services_types))
#     print("Entities mentioned: " + str(entities))
#     print("Addresses: " + str(addresses))