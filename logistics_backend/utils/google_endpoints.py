import requests
from pprint import pprint

class PlaceRepository:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://maps.googleapis.com/maps/api/place'
        self.distance_matrix_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    def get_places(self, query):
        """Fetches place predictions based on a text query."""
        try:
            url = f'{self.base_url}/autocomplete/json'
            params = {
                'input': query,
                'key': self.api_key,
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            # print(data)

            if data['status'] == 'OK':
                return [{'description': prediction['description'], 'place_id': prediction['place_id']} for prediction in data['predictions']]
            else:
                raise Exception(data.get('error_message', 'Error fetching places'))
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_lat_lng_and_type_from_place_id(self, place_id):
        """Fetches the latitude, longitude, and place type (e.g., city, town, village) for a given place ID."""
        try:
            url = f'{self.base_url}/details/json'
            params = {
                'place_id': place_id,
                'key': self.api_key,
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data['status'] == 'OK':
                # Extract location
                location = data['result']['geometry']['location']
                lat = location['lat']
                lng = location['lng']

                # Extract types
                place_types_list = data['result']['address_components']
                place_types = set()
                for sub_place_type_list in place_types_list:
                    for sub_place_type in sub_place_type_list['types']:
                        place_types.add(sub_place_type)
                # pprint(place_types)
                # pprint(data['result']['address_components'])

                # Determine if it's a city, town, or village based on the types
                if 'sublocality_level_1' in place_types or 'neighborhood' in place_types:
                    place_type = 'city'
                elif 'administrative_area_level_3' in place_types:
                    place_type = 'town'
                elif 'locality' in place_types:
                    place_type = 'village'
                else:
                    place_type = 'village'

                return lat, lng, place_type
            else:
                raise Exception(data.get('error_message', 'Error fetching location details'))
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_distance_and_time(self, origin_lat, origin_lng, destination_lat, destination_lng, mode='driving'):
        """Fetches distance and time between two coordinates in the specified mode (default: driving)."""
        try:
            url = self.distance_matrix_url
            params = {
                'origins': f'{origin_lat},{origin_lng}',
                'destinations': f'{destination_lat},{destination_lng}',
                'mode': mode,
                'key': self.api_key,
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data['status'] == 'OK':
                element = data['rows'][0]['elements'][0]
                
                if element['status'] == 'OK':
                    
                    # distance_text = element['distance']['text']
                    # duration_text = element['duration']['text']
                    # print(f"{element['distance']}, {element['duration']}")
                    
                    distance = element['distance']['value']
                    duration = element['duration']['value']
                    
                    return distance, duration
                else:
                    raise Exception(f"Error in distance matrix response: {element['status']}")
            else:
                raise Exception(data.get('error_message', 'Error fetching distance and time'))
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_place_id_from_coordinates(self, latitude, longitude):
        """Fetches the place_id for given coordinates using reverse geocoding."""
        try:
            url = f'https://maps.googleapis.com/maps/api/geocode/json'
            params = {
                'latlng': f'{latitude},{longitude}',
                'key': self.api_key,
            }
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data['status'] == 'OK' and data['results']:
                # pprint(data['results'])
                place_id = data['results'][0]['place_id']
                location_name = data['results'][0]['formatted_address']
                return place_id, location_name
            
            else:
                raise Exception(data.get('error_message', 'Error fetching place_id from coordinates'))
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")

# Example usage:
# place_repo = PlaceRepository(api_key)
# # predictions = place_repo.get_places('Sir MVIT College Bangalore')
# # predictions = place_repo.get_places('Devi sthan Ranipur korara')
# # predictions = place_repo.get_places('Bhartiya City Mall Bangalore')
# predictions = place_repo.get_places('DPS Patna')
# pprint(predictions)
# lat, lng, place_type = place_repo.get_lat_lng_and_type_from_place_id('ChIJDeAa3y0ZrjsRXDGT6m0MFQo')
# lat, lng, place_type = place_repo.get_lat_lng_and_type_from_place_id('ChIJ6VdwNgBHjTkRBTIqd0D13cE')
# lat1, lng1, place_type = place_repo.get_lat_lng_and_type_from_place_id('EjNCaGFydGl5YSBDaXR5LCBLYW5udXJ1LCBCZW5nYWx1cnUsIEthcm5hdGFrYSwgSW5kaWEiLiosChQKEgmHfUtX7RmuOxEGbxaxPqq0vRIUChIJTXj_EogZrjsROMu0N3k1jYE')
# print(f"Location: {lat, lng}, Type: {place_type}")

# distance, duration = place_repo.get_distance_and_time(lat, lng, lat1, lng1)
# print(f"Distance: {distance}, Duration: {duration}")

# place_id, location_name = place_repo.get_place_id_from_coordinates(25.2654312, 84.7074619)
# print(f"Place ID: {place_id}, Location Name: {location_name}")
