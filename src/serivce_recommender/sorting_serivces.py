#########
import openrouteservice
from openrouteservice import convert
import os
from dotenv import load_dotenv
import datetime 
import ast
import logging
from colorlog import ColoredFormatter
logging.getLogger().handlers = []  # Remove any existing handlers
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(log_color)s%(levelname)-8s%(reset)s %(message)s'))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.DEBUG)
load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")
client = openrouteservice.Client(key=ORS_API_KEY) # Specify your personal API key 




def getTimeDay():
    current_time = datetime.datetime.now()     
    if current_time.hour>12:
        hour= current_time.hour%12
        return str(hour)+' p.m',current_time.strftime("%A")
    return str(current_time.hour)+' a.m', current_time.strftime("%A")

def getCurrentbusy(dictionery,Time):
    if Time in dictionery:
        if dictionery[Time]==0:
            return 1
        return dictionery[Time]
    return 1


def get_OccpancyFactors(result):
    time ,day =getTimeDay()
    occpancyFactors=[]
    for document in result:
        # logging.debug(getCurrentbusy(document[day], '10 a.m'))
        occpancyFactors.append(getCurrentbusy(document[day], time))
    return occpancyFactors

def get_travelDurations(longitude,latitude ,result, profile='driving-car'):

    print(f"result {result}")
    sources=[0]
    destinations=[]
    locations=[]
    locations.append([longitude,latitude])
    for entity in result:
        locations.append(entity['location']['coordinates'])
    
    destinations=[ i for i in range(len(sources), len(locations) )]
    logging.debug(f'sources: {sources}')
    logging.debug(f'destinations: {destinations}')
    logging.debug(f'locations: {locations}')
    logging.debug(f'profile: {profile}')

    geometry=client.distance_matrix(locations ,profile=profile, sources=sources, destinations=destinations)
    logging.debug(geometry)
    return geometry['durations'][0]

def get_recommendedSerivce(longitude,latitude ,result, preference='Estimated Overall Service Time'):   
    # Load environment variables from .env file
    occpancyFactors= get_OccpancyFactors(result)
    logging.debug(occpancyFactors)
    #########
    #########
    durations =get_travelDurations(longitude,latitude ,result)
    logging.debug(durations)
    #########
    minutes=5
    serviceTime=60*minutes
    Estimated_serviceTime= [(x*serviceTime) + y for x, y in zip(occpancyFactors,durations)]
    #########
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for  dic in result:
        del dic["Unnamed: 0"]
        del dic['_id']
        del dic['Service URL']
        # del dic['Service Type']
        del dic['About']
        for day in weekdays:
            del dic[day]
        del dic['Opening/Closing Time']
        del dic['Latitude']
        del dic['Longitude']
        del dic['location']
        del dic['collection_name']
    #########
    return result
    # for x,y in zip(result, occpancyFactors):
    #     x["Occupancy"] = y 
    # for x,y in zip(result, durations):
    #     x["Estimated Travel Time"] = y/60 
    # for x,y in zip(result, Estimated_serviceTime):
    #     x["Estimated Overall Service Time"] = y/60 

    # import pandas as pd
    # df= pd.DataFrame(result)
    # logging.debug(df.head())
    # if preference !="Rate":
    #     min_index = df[preference].idxmin()
    #     # Getting the row with the minimum value
    #     row_with_min_value = df.loc[min_index]
    #     return row_with_min_value.to_dict()
    # elif preference == "Rate":
    #     max_index = df[preference].idxmax()
    #     # Getting the row with the minimum value
    #     row_with_max_value = df.loc[max_index]
    #     return row_with_max_value.to_dict()



# ResponseInJson=get_recommendedSerivce(longitude,latitude ,result, preference="Rate")