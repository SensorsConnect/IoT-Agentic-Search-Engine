import requests
import os
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY") 
osm_api_key = os.environ.get("ORS_API_KEY")  # Not needed for OSRM, but could be used for other OSM services

class GoogleMapsTextSearchClient:
    def __init__(self, google_api_key=None, osm_api_key=None):
        self.google_api_key = google_api_key
        self.osm_api_key = osm_api_key  # OSRM does not require an API key, but added for extensibility
        # Updated to use the newer Places API endpoint (nearbysearch or textsearch)
        self.nearby_search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.text_search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        self.osrm_url = "http://router.project-osrm.org/table/v1/driving/"
    
    def text_search(self, query, limit=3, latitude=None, longitude=None, radius=50000):
        print("Origin coordinates:", latitude, longitude)
        print("Search query:", query)

        # If location is provided, use nearbysearch with keyword for better location-based results
        if latitude is not None and longitude is not None:
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius,
                'keyword': query,
                'key': self.google_api_key
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

    def nearby_search_ranked_by_distance(self, query, latitude, longitude, limit=5):
        """Search nearby places ranked by distance (nearest first)."""
        params = {
            'location': f"{latitude},{longitude}",
            'rankby': 'distance',
            'keyword': query,
            'key': self.google_api_key
        }
        print(f"Using nearby search (rankby=distance) with params: {params}")

        response = requests.get(self.nearby_search_url, params=params)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            results = response_data.get('results', [])
            status = response_data.get('status', 'UNKNOWN')
            print(f"API Status: {status}, Results: {len(results)}")

            if status != 'OK' and status != 'ZERO_RESULTS':
                print(f"API returned status: {status}")
                if 'error_message' in response_data:
                    print(f"Error message: {response_data['error_message']}")

            return results[:limit]
        else:
            print("Error occurred:", response.content)
            response.raise_for_status()

    def get_travel_times(self, origin_latitude, origin_longitude, destinations):
        """
        Calculate travel times from the origin to multiple destinations using OSRM.
        
        :param origin_latitude: Latitude of the origin.
        :param origin_longitude: Longitude of the origin.
        :param destinations: List of (latitude, longitude) tuples for the destinations.
        :return: List of travel times in minutes.
        """
        # Validate inputs - OSRM requires at least 2 coordinates (origin + destination)
        if not destinations or len(destinations) == 0:
            print("No destinations provided for travel time calculation - OSRM requires at least one destination")
            return []
        
        # Build coordinates string: origin;dest1;dest2;...
        coords = f"{origin_longitude},{origin_latitude}"
        for lat, lon in destinations:
            coords += f";{lon},{lat}"
        
        # Build URL with proper formatting (no trailing semicolon)
        url = f"{self.osrm_url}{coords}"
        params = {
            'annotations': 'duration'
        }
        print(f"OSRM Request URL: {url}")
        print(f"OSRM Request params: {params}")
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            durations = data.get('durations', [[]])[0][1:]  # Skip the first value as it is the origin to origin
            travel_times = [duration / 60 for duration in durations]  # Convert seconds to minutes
            return travel_times
        except requests.exceptions.HTTPError as e:
            print(f"OSRM HTTP Error: {e}")
            print(f"Response content: {response.content}")
            # Return N/A for all destinations if OSRM fails
            return ['N/A'] * len(destinations)
        except Exception as e:
            print(f"OSRM Error: {e}")
            return ['N/A'] * len(destinations)

    def get_photo_url(self, photo_reference, max_width=400):
        """Build a Google Places photo URL from a photo_reference. No API call."""
        if not photo_reference:
            return None
        return (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth={max_width}&photo_reference={photo_reference}&key={self.google_api_key}"
        )

    def get_place_details(self, place_id, fields=None):
        """Fetch place details from the Place Details API."""
        if not place_id:
            return {}
        if fields is None:
            fields = ["formatted_phone_number", "website"]
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": ",".join(fields),
            "key": self.google_api_key,
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json().get("result", {})
        except Exception as e:
            print(f"Place Details API error: {e}")
        return {}

    def get_formatted_address(self, place):
        # If already present in the search result, use it
        addr = (place.get('formatted_address') or
                place.get('formattedAddress') or
                place.get('vicinity'))
        if addr:
            return addr

        # Otherwise, fetch via Place Details with fields=formatted_address
        place_id = place.get('place_id') or place.get('id')
        if not place_id:
            return None
        details = self.place_details(place_id, fields=['formatted_address'])  # make sure your method passes fields
        result = details.get('result') or details.get('place') or {}
        return result.get('formatted_address') or result.get('formattedAddress')

    def text_search_with_details(self, query, origin_latitude, origin_longitude, limit=3, radius=50000):
        # Use user's location coordinates to bias the search results
        print("Origin coordinates:", origin_latitude, origin_longitude)
        places = self.text_search(query, limit, latitude=origin_latitude, longitude=origin_longitude, radius=radius)
        
        # Check if we got any places from the search
        if not places or len(places) == 0:
            print("No places found from text search - returning empty results")
            return []
        
        destinations = [
            (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
            for place in places
        ]
        
        # Get travel times for all destinations in one call
        travel_times = self.get_travel_times(origin_latitude, origin_longitude, destinations)
        
        places_with_details = []
        for i, place in enumerate(places):
            name = place.get('name', 'N/A')
            address = self.get_formatted_address(place)
            print(f"Extracted address for {name}: {address}")
            rating = place.get('rating', 'N/A')
            places_with_details.append({
                'entity_name': name,
                'address': address,
                'rate': rating,
                'estimated_travel_time': f"{travel_times[i]:.2f} mins" if travel_times[i] != 'N/A' else 'N/A'
            })
        
        return places_with_details


# Example usage:
gmaps_text_search_client = GoogleMapsTextSearchClient(GOOGLE_MAPS_API_KEY, osm_api_key)
# results = gmaps_text_search_client.text_search_with_details("best coffee shops in San Francisco", 37.7749, -122.4194, limit=3)
# print(results)
