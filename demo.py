# # # # # #
# DEPRECATED (For most part)
# Older version of pipeline, running each phase of pipeline on EVERY store before moving on.
# Some recent commits main contain updates to t his due to easier progammability for some members of the team
# Most changes are put into main.py/store.py after
# # # # # #


from google.cloud import vision
import os
import sys

from detect_text import any_text_triggering
from places import get_places, load_zipcodes
from places import get_places, get_place_details, load_zipcodes
from streetview import get_streetview_image
from store import Store
from vision import extract_image_text
from web_scraping import search_key_terms


def main():
    images_dir = 'streetview_images'
    # Zipcodes being considered (All for Louisville Metro Area)
    zipcodes = load_zipcodes('D:/Git/Capstone/capstone-poc/louisville_metro_zipcodes.txt')
    # Store types being considered
    store_types = ['tobacco', 'smoke', 'vaporizer', 'cannabis', 'store', 'shop',
                   'pharmacy', 'health', 'beauty']
    # Trigger phrases (just a few simple "within" examples)
    trigger_phrases = ['marlboro', 'camel', 'newport', 'wave', 'vape', 'tobacco',
                       'smoke', 'cigarette', 'fog', 'cigar', 'cloud', 'vapor']

    # Get places for all store types in all zipcodes
    print('Getting places... ', end='')
    sys.stdout.flush()
    # NOTE: Current simplistic search method may have overlap (same place appearing multiple times)
    #
    # Just testing for now, so only use first zipcode with each store type (way too many API calls otherwise)
    #
    #
    stores = []
    for zipcode in zipcodes[:1]:
        for store_type in store_types[:1]:
            query = f'{store_type}+in+{zipcode}'
            for place in get_places(query):
                stores.append(Store(place))

    print(f'Done [{len(stores)} stores]')
    #print(places[0])

    # Get streetview images for each place returned
    print('Getting streetview images... ', end='')
    sys.stdout.flush()
    if not os.path.isdir(images_dir):
        os.mkdir(images_dir)
    for store in stores:
        image = get_streetview_image(store.place['formatted_address'])
        if image is None:
            name = place['name']
            print(f'ERROR: Unable to retrieve streetview image for {name}')
            continue
        image_path = '{dir}/{place_id}.jpg'.format(
            dir=images_dir,
            place_id=store.place['place_id'])
        with open(image_path, 'wb') as f:
            f.write(image)
        store.image_path = image_path
    print(f'Done')

    # Retrieve advanced details
    print('Retrieving advanced details...', end='')
    sys.stdout.flush()
    for store in stores:
        details = get_place_details(store.place['place_id'])
        if details is None:
            print('ERROR: Failed to retrieve details for place', store.place['place_id'])
            continue
        store.photos = details['photos']
        store.reviews = details['reviews']
        if 'website' in details:
            store.website = details['website']
    print('Done')
    
    print('Saving all images')
    # Extract text from images
    print('Extracting text from images... ', end='')
    sys.stdout.flush()
    for store in stores:
        store.image_text = extract_image_text(store.image_path)
    print(f'Done')
    
    # TODO: Should also check business name against trigger phrases
    # Check descriptions against trigger words
    print('Checking if store names or extracted text is triggering...', end='')
    sys.stdout.flush()
    # Writing descriptions to file for testing review
    desc_file = open('descriptions.txt', 'w', encoding='utf-8')
    for store in stores:
        name = store.place['name']
        descriptions = store.image_text[1:] #The first index is a the unparsed string, white [1:n] is that same string, split by \n.
        #Getting all information from store.reviews()
        strings = [name] + descriptions + sum([x['text'].split(' ') for x in store.reviews], [])
        # Writing to file for review while testing
        desc_file.write(','.join(strings) + '\n')
        store.is_triggering = any_text_triggering(strings, trigger_phrases)
    desc_file.close()
    print(f'Done')
    
    # Group places with possible indicators and without
    print('Grouping results... ', end='')
    sys.stdout.flush()
    places_with_indicators = []
    places_without_indicators = []
    for store in stores:
        # Save store info and images
        store.save()
        if store.is_triggering:
            places_with_indicators.append(store)
        else:
            places_without_indicators.append(store)
    print(f'Done [{len(places_with_indicators)} w/ indicators] [{len(places_without_indicators)} w/o indicators]')
    
    # Print results
    print(f'Places with possible indicators:', [store.place['name'] for store in places_with_indicators])
    print(f'\nPlaces without possible indicators:', [store.place['name'] for store in places_without_indicators])



if __name__ == '__main__':
    main()