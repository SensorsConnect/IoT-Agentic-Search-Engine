import ssl
import logging
from colorlog import ColoredFormatter
from typing import Union, Optional

from fastapi import ( FastAPI, Request)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from graph import runnable

# Reset the logging configuration to ensure only the new settings apply
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

handler = logging.StreamHandler()
# Configure logging to show only INFO level and higher
handler.setFormatter(ColoredFormatter('%(log_color)s%(levelname)-8s%(reset)s %(message)s'))
logging.basicConfig(level=logging.INFO)
# logging.disable()
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
    # logging.getLogger().handlers = []  # Remove any existing handlers
    # handler = logging.StreamHandler()
    # handler.setFormatter(ColoredFormatter('%(log_color)s%(levelname)-8s%(reset)s %(message)s'))
    # logging.getLogger().addHandler(handler)
# Configure logging to show only INFO level and higher

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


class LocationData(BaseModel):
    latitude: float
    longitude: float

class Query(BaseModel):
    text: str
    threadId: str
    location: Optional[LocationData] = None


@app.get("/")

async def root(request: Request):
    """Root endpoint returning basic API information."""
    return {
        "name": "WebAssistant",
        "version": "1.0.0",
        "status": "healthy",
        "environment": "development",
        "swagger_url": "/docs"
    }


@app.put("/query")
def query_handler(query: Query):
    print(f"Query received: {query.text}")
    print(f"Thread ID: {query.threadId}")
    
    if query.location:
        print(f"Location data: lat={query.location.latitude}, lng={query.location.longitude}")
        logging.info(f"User location: {query.location.latitude}, {query.location.longitude}")
    else:
        print("No location data provided")
        logging.info("No user location data available")

    thread = {"configurable": {"thread_id": query.threadId}}

    # Include location context in the message if available
    message_content = query.text
    if query.location:
        message_content += f"\n\n[User Location: {query.location.latitude}, {query.location.longitude}]"

    human_message = HumanMessage(content=message_content)
    messages = [human_message]

    result = runnable.invoke({"messages":messages}, thread)
    print(result["response"][-1])

    return {"answer": result["response"][-1]}



def printResults(results):
    services_name_addresses=[]
    for result in results:
        logging.info(result['Service Address'])
        logging.info(result['Service Name'])
        logging.info(result['location']['coordinates'])
        services_name_addresses.append([result['Service Name'],result['Service Address']])
    return services_name_addresses
