import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

class LocationFinder:
    def __init__(self, user_agent="geo_locator"):
        self.geolocator = Nominatim(user_agent=user_agent)
    
    def get_country_from_city(self, city):
        location = self.get_location_from_address(city)
        if location:
            return self.get_country_from_coordinates(location[0], location[1])
        return None
    
    def get_location_from_address(self, address):
        try:
            location = self.geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            else:
                return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Error: {e}")
            return None
    
    def get_address_from_coordinates(self, latitude, longitude):
        try:
            location = self.geolocator.reverse((latitude, longitude), exactly_one=True)
            if location:
                return location.address
            else:
                return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"Error: {e}")
            return None
    
    def get_country_city_from_address(self, address):
        location = self.get_location_from_address(address)
        if location:
            return self.get_country_city_from_coordinates(location[0], location[1])
        return None
    
    def get_country_city_from_coordinates(self, latitude, longitude):
        address = self.get_address_from_coordinates(latitude, longitude)
        if address:
            address_details = address.split(", ")
            if len(address_details) >= 3:
                city = address_details[-3]
                country = address_details[-1]
                return city, country
            else:
                return None
        return None
    
    def get_city_from_coordinates(self, latitude, longitude):
        address = self.get_address_from_coordinates(latitude, longitude)
        if address:
            address_details = address.split(", ")
            if len(address_details) >= 3:
                city = address_details[-3]  # Extracting the city part
                return city
            else:
                return None
        return None
    
    def get_country_from_coordinates(self, latitude, longitude):
        address = self.get_address_from_coordinates(latitude, longitude)
        if address:
            address_details = address.split(", ")
            if len(address_details) >= 2:
                country = address_details[-1]  # Extracting the country part
                return country
            else:
                return None
        return None

    def process_location_query(self, location_data):
        # Check if any location data is provided
#         if not any([location_data["city"], location_data["country"], location_data["address"], location_data["coordinates"] != [0, 0]]):
#             return False
        
        result = {
            "city": None,
            "country": None,
            "coordinates": None
        }
        
        if location_data["city"]:
            result["city"] = location_data["city"]
            country = self.get_country_from_city(location_data["city"])
            if country:
                result["country"] = country
                coords = self.get_location_from_address(location_data["city"])
                if coords:
                    result["coordinates"] = coords
            else:
                return False
        
        elif location_data["address"]:
            country_city = self.get_country_city_from_address(location_data["address"])
            if country_city:
                result["city"], result["country"] = country_city
                coords = self.get_location_from_address(location_data["address"])
                if coords:
                    result["coordinates"] = coords
            else:
                return False
        
        elif location_data["coordinates"] != [0, 0]:
            print( location_data["coordinates"] )
            latitude, longitude = location_data["coordinates"]
            country_city = self.get_country_city_from_coordinates(latitude, longitude)
            if country_city:
                result["city"], result["country"] = country_city
                result["coordinates"] = (latitude, longitude)
            else:
                return  {
                    "city": None,
                    "country": None,
                    "coordinates": location_data["coordinates"] 
                    }
        
        else:
            return False
        
        return result

# Example usage
finder = LocationFinder()

# json_data = """
# {
#   "query-type": "service-recommendation",
#   "service": "coffee shop",
#   "city": "Vancouver",
#   "country": "",
#   "address": "",
#   "coordinates": [34.648529,-51.6013529],
#   "question": "I want to drink coffee in a place close to me"
# }
# """

# location_data = json.loads(json_data)

# result = finder.process_location_query(location_data)
# print(result)

