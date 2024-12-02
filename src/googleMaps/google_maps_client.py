import requests
import os
Google_Maps_API_Key = os.environ.get("Google_Maps_API_Key") 
osm_api_key = os.environ.get("ORS_API_KEY")  # Not needed for OSRM, but could be used for other OSM services

class GoogleMapsTextSearchClient:
    def __init__(self, google_api_key=None, osm_api_key=None):
        self.google_api_key = google_api_key
        self.osm_api_key = osm_api_key  # OSRM does not require an API key, but added for extensibility
        self.text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.osrm_url = "http://router.project-osrm.org/table/v1/driving/"
    
    def text_search(self, query, limit=3):
        params = {
            'query': query,
            'key': self.google_api_key
        }
        response = requests.get(self.text_search_url, params=params)
        if response.status_code == 200:
            results = response.json().get('results', [])
            # Limit the number of results to the specified limit
            return results[:limit]
        else:
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
        places = self.text_search(query, limit)
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
