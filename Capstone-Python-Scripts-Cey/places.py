# Interface with Google Places API 
# Please set up your environemnt first with info in documentation
#
import dotenv
import os
import requests
import json

dotenv.load_dotenv()


def load_zipcodes(path):
    with open(path, 'r') as f:
        zipcodes = f.read().split('\n')
    return zipcodes

# GET info from API with query, recieves list of google places.
# https://developers.google.com/maps/documentation/places/web-service/search-text
# https://developers.google.com/maps/documentation/places/web-service/text-search -> probably s hould udpate for new version?
def get_places(query):
    api_key = os.getenv('MAPS_API_KEY')
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={api_key}'
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f'ERROR: request to Maps Places API failed with status code {resp.status_code}')
        return None
    data = resp.json()  
    return data['results']

#def get_website(id):
    #api_key = os.getenv('MAPS_API_KEY')
    #url = f'https://maps.googleapis.com/maps/api/place/details/json?fields=website&place_id={id}&key={api_key}'
    #data = resp.json()
    #return data['results']


# GET additioanl information. See goo
# https://developers.google.com/maps/documentation/places/web-service/details
def get_place_details(place_id, fields=['website', 'reviews', 'photos']):
    api_key = os.getenv('MAPS_API_KEY')
    base_url = f'https://maps.googleapis.com/maps/api/place/details/json?'
    fields_params = '%2C'.join(fields)
    url = f'{base_url}fields={fields_params}&place_id={place_id}&key={api_key}'
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f'ERROR: request to Maps Places API failed with status code {resp.status_code}')
        return None
    data = resp.json()
    return data['result']
# GET photo data from photo_id provided from get_place_details()
# https://developers.google.com/maps/documentation/places/web-service/photos
# Also updated -> https://developers.google.com/maps/documentation/places/web-service/place-photos
def get_place_photo(photo_id, max_width = 640):
    api_key = os.getenv('MAPS_API_KEY')
    base_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}'
    url = f'{base_url}&photo_reference={photo_id}&key={api_key}'
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f'ERROR: request to Maps Places API failed with status code {resp.status_code}')
    return resp.content

# Test Case
def test_get_place_details():
    place_id = 'ChIJ-R0krlhsaYgRnnahJBqBC9M'
    try:
        details = get_place_details(place_id)
        for key in {'photos', 'reviews', 'website'}:
            if key not in details:
                print(f'Key "{key}" not in details result!')
                return False
            if key == 'photos':
                photo_content = get_place_photo(details['photos'][0]['photo_reference'])
            if key == 'reviews':
                text = sum([x['text'].split(' ') for x in details['reviews']], [])
        return True
    except Exception as e:
        print(e)
        return False

# yeah
def test():
    test_get_place_details()

# okay
if __name__ == '__main__':
    test()