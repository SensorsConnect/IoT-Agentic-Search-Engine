import logging
import time
import requests
import os

logger = logging.getLogger(__name__)

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
        logger.info(f"[DEBUG text_search] START query='{query}', lat={latitude}, lon={longitude}, radius={radius}, limit={limit}")
        t0 = time.time()

        # If location is provided, use nearbysearch with keyword for better location-based results
        if latitude is not None and longitude is not None:
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius,
                'keyword': query,
                'key': self.google_api_key
            }
            url = self.nearby_search_url
        else:
            params = {
                'query': query,
                'key': self.google_api_key
            }
            url = self.text_search_url

        try:
            response = requests.get(url, params=params, timeout=10)
        except requests.exceptions.Timeout:
            logger.error(f"[DEBUG text_search] TIMEOUT after 10s for query='{query}'")
            return []
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[DEBUG text_search] CONNECTION ERROR: {e}")
            return []
        except Exception as e:
            logger.error(f"[DEBUG text_search] UNEXPECTED ERROR: {type(e).__name__}: {e}")
            return []

        elapsed = time.time() - t0
        logger.info(f"[DEBUG text_search] HTTP {response.status_code} in {elapsed:.2f}s")

        if response.status_code == 200:
            response_data = response.json()
            results = response_data.get('results', [])
            status = response_data.get('status', 'UNKNOWN')
            logger.info(f"[DEBUG text_search] API status='{status}', results_count={len(results)}")

            if status not in ('OK', 'ZERO_RESULTS'):
                err_msg = response_data.get('error_message', 'N/A')
                logger.error(f"[DEBUG text_search] API ERROR status='{status}', error_message='{err_msg}'")

            return results[:limit]
        else:
            logger.error(f"[DEBUG text_search] HTTP ERROR {response.status_code}: {response.content[:500]}")
            response.raise_for_status()

    def nearby_search_ranked_by_distance(self, query, latitude, longitude, limit=5):
        """Search nearby places ranked by distance (nearest first)."""
        logger.info(f"[DEBUG nearby_search] START query='{query}', lat={latitude}, lon={longitude}, limit={limit}")
        t0 = time.time()
        params = {
            'location': f"{latitude},{longitude}",
            'rankby': 'distance',
            'keyword': query,
            'key': self.google_api_key
        }

        try:
            response = requests.get(self.nearby_search_url, params=params, timeout=10)
        except requests.exceptions.Timeout:
            logger.error(f"[DEBUG nearby_search] TIMEOUT after 10s for query='{query}'")
            return []
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[DEBUG nearby_search] CONNECTION ERROR: {e}")
            return []
        except Exception as e:
            logger.error(f"[DEBUG nearby_search] UNEXPECTED ERROR: {type(e).__name__}: {e}")
            return []

        elapsed = time.time() - t0
        logger.info(f"[DEBUG nearby_search] HTTP {response.status_code} in {elapsed:.2f}s")

        if response.status_code == 200:
            response_data = response.json()
            results = response_data.get('results', [])
            status = response_data.get('status', 'UNKNOWN')
            logger.info(f"[DEBUG nearby_search] API status='{status}', results_count={len(results)}")

            if status not in ('OK', 'ZERO_RESULTS'):
                err_msg = response_data.get('error_message', 'N/A')
                logger.error(f"[DEBUG nearby_search] API ERROR status='{status}', error_message='{err_msg}'")

            for i, r in enumerate(results[:limit]):
                logger.info(f"[DEBUG nearby_search] result[{i}]: name='{r.get('name')}', rating={r.get('rating')}, place_id={r.get('place_id','')[:20]}")
            return results[:limit]
        else:
            logger.error(f"[DEBUG nearby_search] HTTP ERROR {response.status_code}: {response.content[:500]}")
            response.raise_for_status()

    def get_travel_times(self, origin_latitude, origin_longitude, destinations):
        """
        Calculate travel times from the origin to multiple destinations using OSRM.
        """
        logger.info(f"[DEBUG OSRM] START origin=({origin_latitude},{origin_longitude}), destinations_count={len(destinations) if destinations else 0}")
        t0 = time.time()

        if not destinations or len(destinations) == 0:
            logger.warning("[DEBUG OSRM] No destinations provided, returning empty")
            return []

        # Build coordinates string: origin;dest1;dest2;...
        coords = f"{origin_longitude},{origin_latitude}"
        for lat, lon in destinations:
            coords += f";{lon},{lat}"

        url = f"{self.osrm_url}{coords}"
        params = {'annotations': 'duration'}

        try:
            response = requests.get(url, params=params, timeout=10)
            elapsed = time.time() - t0
            logger.info(f"[DEBUG OSRM] HTTP {response.status_code} in {elapsed:.2f}s")
            response.raise_for_status()

            data = response.json()
            osrm_code = data.get('code', 'N/A')
            logger.info(f"[DEBUG OSRM] OSRM code='{osrm_code}'")

            if osrm_code != 'Ok':
                logger.error(f"[DEBUG OSRM] OSRM returned non-Ok code: {osrm_code}, message: {data.get('message', 'N/A')}")
                return ['N/A'] * len(destinations)

            durations = data.get('durations', [[]])[0][1:]
            travel_times = [duration / 60 for duration in durations]
            for i, tt in enumerate(travel_times):
                logger.info(f"[DEBUG OSRM] dest[{i}] travel_time={tt:.2f} mins")
            return travel_times
        except requests.exceptions.Timeout:
            elapsed = time.time() - t0
            logger.error(f"[DEBUG OSRM] TIMEOUT after {elapsed:.2f}s")
            return ['N/A'] * len(destinations)
        except requests.exceptions.ConnectionError as e:
            elapsed = time.time() - t0
            logger.error(f"[DEBUG OSRM] CONNECTION ERROR after {elapsed:.2f}s: {e}")
            return ['N/A'] * len(destinations)
        except requests.exceptions.HTTPError as e:
            elapsed = time.time() - t0
            logger.error(f"[DEBUG OSRM] HTTP ERROR after {elapsed:.2f}s: {e}, body: {response.content[:500]}")
            return ['N/A'] * len(destinations)
        except Exception as e:
            elapsed = time.time() - t0
            logger.error(f"[DEBUG OSRM] UNEXPECTED ERROR after {elapsed:.2f}s: {type(e).__name__}: {e}")
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
        logger.info(f"[DEBUG place_details] START place_id='{place_id}', fields={fields}")
        t0 = time.time()
        if not place_id:
            logger.warning("[DEBUG place_details] No place_id provided, returning empty")
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
            response = requests.get(url, params=params, timeout=10)
            elapsed = time.time() - t0
            logger.info(f"[DEBUG place_details] HTTP {response.status_code} in {elapsed:.2f}s")
            if response.status_code == 200:
                result = response.json().get("result", {})
                logger.info(f"[DEBUG place_details] Got fields: {list(result.keys())}")
                return result
            else:
                logger.error(f"[DEBUG place_details] HTTP ERROR {response.status_code}: {response.content[:500]}")
        except requests.exceptions.Timeout:
            logger.error(f"[DEBUG place_details] TIMEOUT after {time.time() - t0:.2f}s")
        except Exception as e:
            logger.error(f"[DEBUG place_details] ERROR: {type(e).__name__}: {e}")
        return {}

    def get_formatted_address(self, place):
        name = place.get('name', 'unknown')
        # If already present in the search result, use it
        addr = (place.get('formatted_address') or
                place.get('formattedAddress') or
                place.get('vicinity'))
        if addr:
            logger.info(f"[DEBUG address] Found cached address for '{name}': '{addr[:60]}'")
            return addr

        # Otherwise, fetch via Place Details with fields=formatted_address
        place_id = place.get('place_id') or place.get('id')
        if not place_id:
            logger.warning(f"[DEBUG address] No address or place_id for '{name}', returning None")
            return None
        logger.info(f"[DEBUG address] Fetching address from Place Details API for '{name}' (place_id={place_id[:20]})")
        details = self.get_place_details(place_id, fields=['formatted_address'])
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
