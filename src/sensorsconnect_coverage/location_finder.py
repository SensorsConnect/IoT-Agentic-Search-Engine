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

    
# Example usage
finder = LocationFinder()
# address = "1600 Pennsylvania Avenue NW, Washington, DC"
# coordinates = (43.8908352,-78.8664241)

# # Get location from address
# location = finder.get_location_from_address(address)
# print(f"Location (lat, long) for the address: {location}")

# # Get address from coordinates
# address_from_coords = finder.get_address_from_coordinates(*coordinates)
# print(f"Address from coordinates: {address_from_coords}")

# # Get country and city from address
# country_city = finder.get_country_city_from_address(address)
# print(f"Country and city for the address: {country_city}")

# # Get country and city from coordinates
# country_city_from_coords = finder.get_country_city_from_coordinates(*coordinates)
# print(f"Country and city for the coordinates: {country_city_from_coords}")


# finder.get_country_from_city("Oshawa")