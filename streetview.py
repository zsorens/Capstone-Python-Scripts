import dotenv
import os
import requests

dotenv.load_dotenv()
# # #
# GET requeste Google Maps API for streetview images.
# Content i assume is photo bytes - alvin
def get_streetview_image(location, image_size='640x640'):
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