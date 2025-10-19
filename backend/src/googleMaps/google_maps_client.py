import requests
import os
Google_Maps_API_Key = os.environ.get("Google_Maps_API_Key") 
osm_api_key = os.environ.get("ORS_API_KEY")  # Not needed for OSRM, but could be used for other OSM services

class GoogleMapsTextSearchClient:
    def __init__(self, google_api_key=None, osm_api_key=None):
        self.google_api_key = google_api_key
        self.osm_api_key = osm_api_key  # OSRM does not require an API key, but added for extensibility
        # Updated to use the newer Places API endpoint (nearbysearch or textsearch)
        self.nearby_search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.osrm_url = "http://router.project-osrm.org/table/v1/driving/"
    
    def text_search(self, query, limit=3, latitude=None, longitude=None):
        print("Origin coordinates:", latitude, longitude)
        print("Search query:", query)
        
        # If location is provided, use nearbysearch with keyword for better location-based results
        if latitude is not None and longitude is not None:
            params = {
                'location': f"{latitude},{longitude}",
                'radius': 50000,  # 50km radius (cannot use with rankby)
                'keyword': query,
                'key': self.google_api_key
                # Note: rankby and radius cannot be used together
            }
            url = self.nearby_search_url
            print(f"Using nearby search API with params: {params}")
        else:
            # Fallback to text search without location
            params = {
                'query': query,
                'key': self.google_api_key
            }
            url = self.text_search_url
            print(f"Using text search API with params: {params}")
        
        response = requests.get(url, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("Full API response:", response_data)
            results = response_data.get('results', [])
            status = response_data.get('status', 'UNKNOWN')
            print(f"API Status: {status}")
            print(f"Number of results: {len(results)}")
            
            if status != 'OK' and status != 'ZERO_RESULTS':
                print(f"API returned status: {status}")
                if 'error_message' in response_data:
                    print(f"Error message: {response_data['error_message']}")
            
            # Limit the number of results to the specified limit
            return results[:limit]
        else:
            print("Error occurred:", response.content)
            print("Response status:", response.status_code)
            response.raise_for_status()

    def get_travel_times(self, origin_latitude, origin_longitude, destinations):
        """
        Calculate travel times from the origin to multiple destinations using OSRM.
        
        :param origin_latitude: Latitude of the origin.
        :param origin_longitude: Longitude of the origin.
        :param destinations: List of (latitude, longitude) tuples for the destinations.
        :return: List of travel times in minutes.
        """
        coords = f"{origin_longitude},{origin_latitude};" + ";".join(
            f"{lon},{lat}" for lat, lon in destinations
        )
        url = f"{self.osrm_url}{coords}"
        params = {
            'annotations': 'duration'
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            durations = data.get('durations', [[]])[0][1:]  # Skip the first value as it is the origin to origin
            travel_times = [duration / 60 for duration in durations]  # Convert seconds to minutes
            return travel_times
        else:
            response.raise_for_status()

        return ['N/A'] * len(destinations)

    def text_search_with_details(self, query, origin_latitude, origin_longitude, limit=3):
        # Use user's location coordinates to bias the search results
        print("Origin coordinates:", origin_latitude, origin_longitude)
        places = self.text_search(query, limit, latitude=origin_latitude, longitude=origin_longitude)
        destinations = [
            (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
            for place in places
        ]
        
        # Get travel times for all destinations in one call
        # travel_times = self.get_travel_times(origin_latitude, origin_longitude, destinations)
        
        places_with_details = []
        for place in places:
            name = place.get('name', 'N/A')
            address = place.get('formatted_address', 'N/A')
            rating = place.get('rating', 'N/A')
            places_with_details.append({
                'entity_name': name,
                'address': address,
                'rate': rating,
                # 'estimated_travel_time': f"{travel_time:.2f} mins" if travel_time != 'N/A' else 'N/A'
            })
        
        return places_with_details


# Example usage:
gmaps_text_search_client = GoogleMapsTextSearchClient(Google_Maps_API_Key, osm_api_key)
# results = gmaps_text_search_client.text_search_with_details("best coffee shops in San Francisco", 37.7749, -122.4194, limit=3)
# print(results)
