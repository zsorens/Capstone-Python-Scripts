
import dotenv
import os
import requests

dotenv.load_dotenv()
# # #
# GET requeste Google Maps API for streetview images.
# Content i assume is photo bytes - alvin
"""def get_streetview_image(location, image_size='640x640'):
    api_key = os.getenv('MAPS_API_KEY')
    params = {'key': api_key,
              'location': location,
              'size': image_size}
    base_url = f'https://maps.googleapis.com/maps/api/streetview?'
    resp = requests.get(base_url, params=params)
    if resp.status_code != 200:
        print(f'ERROR: request to Maps API failed with status code {resp.status_code}')
        return None
    if not resp.ok:
        print(f'ERROR: Received a bad response from the Maps API')
        return None
    return resp.content
"""

def get_streetview_image(location, image_size='640x640'):
    api_key = os.getenv('MAPS_API_KEY')
    if not api_key:
        print('ERROR: Missing Google Maps API key. Please set the MAPS_API_KEY environment variable.')
        return None

    params = {'key': api_key,
              'location': location,
              'size': image_size}
    base_url = f'https://maps.googleapis.com/maps/api/streetview?'
    
    try:
        resp = requests.get(base_url, params=params)
        resp.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return resp.content
    except requests.exceptions.RequestException as e:
        print(f'ERROR: Request to Maps API failed: {e}')
        return None