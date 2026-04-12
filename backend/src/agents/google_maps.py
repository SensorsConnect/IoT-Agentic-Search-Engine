import logging
import math
import os
import time
from state_graph import AgentState
from googleMaps.google_maps_client import gmaps_text_search_client
from utils import prepaer_states, llm, parser
from agents_prompt import googlemaps_strategist_prompt
from langchain_core.messages import ToolMessage, HumanMessage

MAX_ITERATIONS = 3


def _parse_travel_time(travel_time_str):
    """Parse travel time string like '5.23 mins' to float. Returns None if N/A or non-finite."""
    if travel_time_str == 'N/A':
        return None
    try:
        val = float(travel_time_str.replace(' mins', ''))
        return val if math.isfinite(val) else None
    except (ValueError, AttributeError):
        return None


def _avg_travel_time(results):
    """Calculate average travel time for a list of results. Returns float('inf') if no valid times."""
    times = [_parse_travel_time(r.get('estimated_travel_time', 'N/A')) for r in results]
    valid_times = [t for t in times if t is not None]
    if not valid_times:
        return float('inf')
    return sum(valid_times) / len(valid_times)


def _build_place_dict(place, travel_time_str):
    """Build a structured place dict from a raw Google Places API result."""
    photo_url = None
    photos = place.get('photos', [])
    if photos:
        ref = photos[0].get('photo_reference')
        if ref:
            photo_url = gmaps_text_search_client.get_photo_url(ref)

    place_id = place.get('place_id', '')
    address = gmaps_text_search_client.get_formatted_address(place)

    # Fetch phone and website from Place Details API (disabled by default — costs ~$0.017/call)
    details = {}
    if os.environ.get("ENABLE_PLACE_DETAILS", "").lower() == "true":
        details = gmaps_text_search_client.get_place_details(place_id, ["formatted_phone_number", "website"])

    def _safe_float(val):
        """Return val if it's a finite float, else None."""
        try:
            f = float(val)
            return f if math.isfinite(f) else None
        except (TypeError, ValueError):
            return None

    return {
        "id": place_id,
        "name": place.get('name', ''),
        "address": address,
        "latitude": _safe_float(place.get('geometry', {}).get('location', {}).get('lat')),
        "longitude": _safe_float(place.get('geometry', {}).get('location', {}).get('lng')),
        "rating": _safe_float(place.get('rating')),
        "photo_url": photo_url,
        "open_now": place.get('opening_hours', {}).get('open_now'),
        "phone": details.get('formatted_phone_number'),
        "website": details.get('website'),
        "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else None,
        "travel_time_min": _parse_travel_time(travel_time_str),
        "source": "google_maps"
    }


def _build_results_from_places(places, lat, lon):
    """Fetch travel times and build detailed result dicts for a list of places."""
    if not places:
        return [], []

    destinations = [
        (place['geometry']['location']['lat'], place['geometry']['location']['lng'])
        for place in places
    ]

    t0 = time.time()
    travel_times = gmaps_text_search_client.get_travel_times(lat, lon, destinations)
    logging.info(f"GoogleMaps OSRM travel_times took {time.time() - t0:.2f}s for {len(destinations)} destinations")

    results = []
    place_dicts = []
    for i, place in enumerate(places):
        name = place.get('name', 'N/A')
        address = gmaps_text_search_client.get_formatted_address(place)
        rating = place.get('rating', 'N/A')
        tt = travel_times[i] if i < len(travel_times) else 'N/A'
        tt_str = f"{tt:.2f} mins" if (tt != 'N/A' and isinstance(tt, (int, float)) and math.isfinite(tt)) else 'N/A'
        results.append({
            'entity_name': name,
            'address': address,
            'rate': rating,
            'estimated_travel_time': tt_str
        })
        place_dicts.append(_build_place_dict(place, tt_str))
    return results, place_dicts


def _sort_by_travel_time(results):
    """Sort results by travel time ascending. N/A goes to the end."""
    def sort_key(r):
        t = _parse_travel_time(r.get('estimated_travel_time', 'N/A'))
        return t if t is not None else float('inf')
    return sorted(results, key=sort_key)


def _sort_places_by_travel_time(places):
    """Sort place dicts by travel_time_min ascending. None goes to end."""
    def sort_key(p):
        t = p.get('travel_time_min')
        return t if t is not None else float('inf')
    return sorted(places, key=sort_key)


def GoogleMaps(state: AgentState):
    agent_start = time.time()
    logging.info("=" * 60)
    logging.info("[DEBUG GoogleMaps] AGENT START")
    location = state.get("location_finder_results", {})
    coordinates = location.get('coordinates', [])
    logging.info(f"[DEBUG GoogleMaps] coordinates={coordinates}, query='{state.get('query', '')[:80]}'")

    # Validate coordinates
    if not coordinates or len(coordinates) < 2:
        logging.error(f"Invalid coordinates received: {coordinates}")
        return prepaer_states({
            "node": "GoogleMaps",
            "call": "generator_agent"
        })

    try:
        lat = float(coordinates[0])
        lon = float(coordinates[1])
    except (ValueError, TypeError) as e:
        logging.error(f"Coordinates are not valid numbers: {e}")
        return prepaer_states({
            "node": "GoogleMaps",
            "call": "generator_agent"
        })

    query = state.get("query", "")
    search_type = state.get("search_type", "text")
    best_results = []
    best_places = []
    best_avg_time = float('inf')
    search_history = []

    for iteration in range(1, MAX_ITERATIONS + 1):
        iter_start = time.time()
        logging.info(f"[DEBUG GoogleMaps] --- Iteration {iteration}/{MAX_ITERATIONS} START ---")

        if iteration == 1:
            t0 = time.time()
            if search_type == "keyword":
                # Brand/chain search: use Text Search API for exact name matching
                places = gmaps_text_search_client.keyword_search(query, lat, lon, limit=5)
                strategy_used = "keyword_search"
                logging.info(f"[DEBUG GoogleMaps] keyword_search took {time.time() - t0:.2f}s, got {len(places or [])} places")
            else:
                # General category search: rank by distance for nearest results
                places = gmaps_text_search_client.nearby_search_ranked_by_distance(query, lat, lon, limit=5)
                strategy_used = "rank_by_distance"
                logging.info(f"[DEBUG GoogleMaps] nearby_search took {time.time() - t0:.2f}s, got {len(places or [])} places")
        else:
            # Use LLM strategist to decide next action
            history_text = ""
            for h in search_history:
                history_text += f"\nIteration {h['iteration']} (strategy: {h['strategy']}):\n"
                if h['results']:
                    for r in h['results']:
                        history_text += f"  - {r['entity_name']}: {r['estimated_travel_time']}, rating: {r['rate']}\n"
                else:
                    history_text += "  No results found.\n"

            prompt = googlemaps_strategist_prompt.format(
                query=query,
                latitude=lat,
                longitude=lon,
                search_history=history_text
            )

            try:
                t0 = time.time()
                logging.info(f"[DEBUG GoogleMaps] Calling LLM strategist...")
                response = llm.invoke([HumanMessage(content=prompt)], timeout=15)
                logging.info(f"[DEBUG GoogleMaps] LLM strategist took {time.time() - t0:.2f}s")
                logging.info(f"[DEBUG GoogleMaps] LLM raw response: {response.content[:200]}")
                decision = parser.parse(response.content)
                logging.info(f"[DEBUG GoogleMaps] Strategist decision: {decision}")
            except Exception as e:
                logging.error(f"[DEBUG GoogleMaps] Strategist LLM ERROR: {type(e).__name__}: {e}")
                break

            action = decision.get("decision", "give_up")

            if action == "accept":
                logging.info("Strategist accepted current results")
                break
            elif action == "give_up":
                logging.info("Strategist gave up")
                break
            elif action == "retry":
                strategy = decision.get("strategy", "narrow_radius")
                strategy_used = strategy
                new_query = decision.get("new_query", query)
                radius = decision.get("radius", 10000)

                if strategy == "narrow_radius":
                    logging.info(f"[DEBUG GoogleMaps] Retry strategy=narrow_radius, new_query='{new_query}', radius={radius}")
                    raw_places = gmaps_text_search_client.text_search(
                        new_query, limit=5, latitude=lat, longitude=lon, radius=radius
                    )
                    logging.info(f"[DEBUG GoogleMaps] narrow_radius got {len(raw_places or [])} places")
                    nr_results, nr_places = _build_results_from_places(raw_places, lat, lon)
                    search_history.append({
                        "iteration": iteration,
                        "strategy": strategy_used,
                        "results": nr_results if nr_results else []
                    })
                    if nr_results:
                        avg = _avg_travel_time(nr_results)
                        if avg < best_avg_time or (avg == float('inf') and not best_results):
                            best_avg_time = avg
                            best_results = nr_results
                            best_places = nr_places
                    continue
                elif strategy == "rephrase_query":
                    logging.info(f"[DEBUG GoogleMaps] Retry strategy=rephrase_query, new_query='{new_query}'")
                    places = gmaps_text_search_client.nearby_search_ranked_by_distance(
                        new_query, lat, lon, limit=5
                    )
                elif strategy == "rank_by_distance":
                    logging.info(f"[DEBUG GoogleMaps] Retry strategy=rank_by_distance, new_query='{new_query}'")
                    places = gmaps_text_search_client.nearby_search_ranked_by_distance(
                        new_query, lat, lon, limit=5
                    )
                elif strategy == "keyword_search":
                    logging.info(f"[DEBUG GoogleMaps] Retry strategy=keyword_search, new_query='{new_query}'")
                    places = gmaps_text_search_client.keyword_search(
                        new_query, lat, lon, limit=5
                    )
                else:
                    logging.info(f"[DEBUG GoogleMaps] Retry strategy='{strategy}' (fallback), new_query='{new_query}'")
                    places = gmaps_text_search_client.nearby_search_ranked_by_distance(
                        new_query, lat, lon, limit=5
                    )
            else:
                break

        # Build results from raw places (iteration 1 and non-narrow_radius retries)
        logging.info(f"[DEBUG GoogleMaps] Building results from {len(places or [])} places...")
        t0 = time.time()
        iteration_results, iteration_places = _build_results_from_places(places, lat, lon)
        logging.info(f"[DEBUG GoogleMaps] _build_results_from_places took {time.time() - t0:.2f}s")

        search_history.append({
            "iteration": iteration,
            "strategy": strategy_used if iteration > 1 else "rank_by_distance",
            "results": iteration_results
        })

        if iteration_results:
            avg = _avg_travel_time(iteration_results)
            if avg < best_avg_time or (avg == float('inf') and not best_results):
                # Accept results even with N/A travel times if we have no better option
                best_avg_time = avg
                best_results = iteration_results
                best_places = iteration_places
                logging.info(f"[DEBUG GoogleMaps] Updated best_results: count={len(best_results)}, avg_travel={avg}")

        logging.info(f"[DEBUG GoogleMaps] --- Iteration {iteration} END (took {time.time() - iter_start:.2f}s) ---")

        # If first iteration got results, decide whether to continue
        if iteration == 1 and best_results:
            # Check if any place has a valid travel time under 15 min
            has_nearby = any(
                (_parse_travel_time(r.get('estimated_travel_time', 'N/A')) or float('inf')) < 15
                for r in best_results
            )
            # Also check if ALL travel times are N/A (OSRM failure) — no point retrying
            all_na = all(
                r.get('estimated_travel_time', 'N/A') == 'N/A'
                for r in best_results
            )
            if has_nearby:
                logging.info("[DEBUG GoogleMaps] Found nearby results on first iteration, skipping strategist")
                break
            if all_na:
                logging.warning("[DEBUG GoogleMaps] OSRM failed for all results — skipping strategist, returning results without travel times")
                break

    # Sort by travel time and return top 3
    total_elapsed = time.time() - agent_start
    logging.info(f"[DEBUG GoogleMaps] AGENT TOTAL TIME: {total_elapsed:.2f}s, best_results_count={len(best_results)}")
    if best_results:
        final_results = _sort_by_travel_time(best_results)[:3]
        final_places = _sort_places_by_travel_time(best_places)[:3]
        for i, r in enumerate(final_results):
            logging.info(f"[DEBUG GoogleMaps] FINAL result[{i}]: {r['entity_name']}, travel={r['estimated_travel_time']}, rating={r['rate']}")
        logging.info("=" * 60)
        return prepaer_states({
            "messages": [ToolMessage(content=str(final_results), name="GoogleMaps", tool_call_id="call_IoT_engine")],
            "node": "GoogleMaps",
            "context": str(final_results),
            "call": "generator_agent",
            "places": final_places
        })
    else:
        logging.warning("[DEBUG GoogleMaps] NO RESULTS found after all iterations")
        logging.info("=" * 60)
        return prepaer_states({
            "node": "GoogleMaps",
            "call": "generator_agent"
        })
