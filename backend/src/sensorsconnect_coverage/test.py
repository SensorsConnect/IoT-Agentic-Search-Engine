# another_script.py
from geography_db import check_city_country_exists, add_country, add_city, close_session

# Add some data (this would typically be done in the main module or setup script)
# add_country('Canada')
# add_city('Toronto', 'Canada')
# add_city('Ottawa', 'Canada')

# Add real data for Ontario, Canada
# add_country('Canada')

# # Adding cities from Ontario
# ontario_cities = [
#     'Toronto',
#     'Ottawa',
#     'Mississauga',
#     'Brampton',
#     'Hamilton',
#     'London',
#     'Markham',
#     'Vaughan',
#     'Kitchener',
#     'Windsor'
# ]

# for city in ontario_cities:
#     add_city(city, 'Canada')

# Example check to see if a city-country pair exists
exists = check_city_country_exists('Toronto', 'Canada')
print(f"(Toronto, Canada) exists: {exists}")

exists = check_city_country_exists('Vancouver', 'Canada')
print(f"(Vancouver, Canada) exists: {exists}")

# Close the session when done
close_session()