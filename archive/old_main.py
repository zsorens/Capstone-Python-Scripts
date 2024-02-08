# # # # # # #
# Depreciated main.py
# Mimics the orignal style of demo.py to batch the stores each stage of pipeline.
# Closely follows demo.py as we used demo,py as an staging envrionment essentially.
#
# # # # # # #


import argparse
from google.cloud import vision
import os
import sys

from detect_text import any_text_triggering
from places import get_places,  get_place_details,  load_zipcodes, get_place_photo
from streetview import get_streetview_image
from store import Store
from vision import extract_image_text
import files
import sql

def load_text(path):
    with open(path, 'r') as f:
        data = f.read().split('\n')
    return data
    

if __name__ == '__main__':
    # Functional Arguments
    #
    parser = argparse.ArgumentParser(description='Pipeline produced by Fall 2023 UofL Capstone Team for Tobacco Permits')
    parser.add_argument('-i', '--images_dir', action='store', default='streetview_images', dest = 'images_dir',
                        help='Directory to save Google Streetview Images to')
    parser.add_argument('-z', '--zip_codes', action='store', default = 'louisville_metro_zipcodes.txt', dest='zip_codes',
                        help='.txt file to read in selected zipcodes to run algorithm for.')
    parser.add_argument('-s','--store_types', action = 'store', default= 'store_types.txt', dest = 'store_types',
                        help='Types of stores to be identified using google places.')
    parser.add_argument('-t','--trigger_phrases', action = 'store', default= 'trigger_phrases.txt', dest = 'trigger_phrases',
                        help='Words that are algorithm will look for to \"Flag\" a store.')
    # Testing Arguments
    # TO-DO: Change "real" to be a limit
    parser.add_argument('-r', '--real', action = 'store_true', dest = 'real',
                        help = 'Run algorithm on entire dataset over just 1 value')
    parser.add_argument('-v', '--verbose', action = 'store_true', dest = 'verbose',
                        help ='Be verbose (print statements)')
    parser.add_argument('-l', '--logging', action = 'store_true',  dest = 'logging',
                        help ='Log progress data')
    parser.add_argument('-ld', '--log_dir', action = 'store', default = 'logs' , dest='log_dir',
                        help = 'Where to log')
    parser.add_argument('-c', '--cache', action = 'store_true', dest='cache',
                        help = 'Save data into database and filese')
    parser.add_argument('-sd', '--store_dir', action = 'store', default = 'store_data', dest = 'store_dir',
                        help='If caching, where to save store data')
    # PULLING ARGS
    #
    #
    #
    args = parser.parse_args()
    images_dir = args.images_dir
    zipcodes = load_text(args.zip_codes)
    store_types = load_text(args.store_types)
    trigger_phrases = load_text(args.trigger_phrases)

    # Get places for all store types in all zipcodes
    if args.verbose:
        print('Getting places... ', end='')
    print('Full version:', args.real)
    sys.stdout.flush()
    # NOTE: Current simplistic search method may have overlap (same place appearing multiple times)
    #
    # args.real is store_true, so if set it will run entire data set, otherwise will not.
    #
    #
    stores = []
    # If
    if not args.real:
        zipcodes = zipcodes[:1]
        store_types = store_types[:1]
    for zipcode in zipcodes:
        for store_type in store_types:
            query = f'{store_type}+in+{zipcode}'
            for place in get_places(query):
                stores.append(Store(place))
    if args.verbose:
        print(f'Done [{len(stores)} stores]')
    #print(places[0])
    # Retrieve advanced details
    if args.verbose:
        print('Retrieving advanced details...', end='')
    sys.stdout.flush()
    for store in stores:
        details = get_place_details(store.place['place_id'])
        if details is None:
            if args.verbose:
                print('ERROR: Failed to retrieve details for place', store.place['place_id'])
            continue
        store.photos = details['photos'] if 'photos' in details else []
        store.reviews = details['reviews'] if 'reviews' in details else []
        if 'website' in details:
            store.website = details['website']
    if args.verbose:
        print('Done')
        
    # Get streetview images for each place returned
    if args.verbose:
        print('Getting streetview images... ', end='')
    sys.stdout.flush()
    if not os.path.isdir(images_dir):
        os.mkdir(images_dir)
    for store in stores:
        image = get_streetview_image(store.place['formatted_address'])
        if image is None:
            name = place['name']
            if args.verbose:
                print(f'ERROR: Unable to retrieve streetview image for {name}')
            continue
        image_path = '{dir}/{place_id}.jpg'.format(
            dir=images_dir,
            place_id=store.place['place_id'])
        with open(image_path, 'wb') as f:
            f.write(image)
        store.image_path = image_path
        if args.verbose:
            print('Done')
            print(f'Getting review images...', end = '')
        review_images_dir = f"{images_dir}/{store.place['place_id']}"
        if not os.path.isdir(review_images_dir):
            os.mkdir(review_images_dir)
        store.review_images = review_images_dir
        for photo in store.photos:
            image_review = get_place_photo(photo['photo_reference'])
            image_path = '{review_images_dir}/{photo_id}.jpg'.format(
                    review_images_dir = review_images_dir,
                    photo_id=photo['photo_reference'])
            with open(image_path, 'wb') as f:
                f.write(image_review)
            if(not args.real):
                break
    if args.verbose:
        print(f'Done')
    # Extract text from images
    if args.verbose:
        print('Extracting text from images... ', end='')
    sys.stdout.flush()
    for store in stores:
        store.image_text = extract_image_text(store.image_path)
    if args.verbose:
        print(f'Done')
        
    
    # TODO: Should also check business name against trigger phrases
    # Check descriptions against trigger words
    if args.verbose:
            print('Checking if store names or extracted text is triggering...', end='')
    sys.stdout.flush()
    # Writing descriptions to file for testing review
    desc_file = open('descriptions.txt', 'w', encoding='utf-8')
    for store in stores:
        name = store.place['name']
        descriptions = store.image_text[1:] if store.image_text else [] #The first index is a the unparsed string, white [1:n] is that same string, split by \n.
        strings = [name] + descriptions + sum([x['text'].split(' ') for x in store.reviews], [])
        # Writing to file for review while testing
        desc_file.write(','.join(strings) + '\n')
        store.is_triggering = any_text_triggering(strings, trigger_phrases)
    desc_file.close()
    if args.verbose:
            print(f'Done')
    
    # Group places with possible indicators and without
    if args.verbose:
        print('Grouping results... ', end='')
    sys.stdout.flush()
    places_with_indicators = []
    places_without_indicators = []
    for store in stores:
        # Save store info and images
        if args.cache:
            store.save(args.store_dir)
        if store.is_triggering:
            places_with_indicators.append(store)
            # Need better logic to store
            # Rather tragic we always do an upsert
            # Also probably move store_to_db somewhere else but for now we'd like it to be in the table first before storing
            sql.store_to_db(store)
            sql.store_flag(store)
        else:
            places_without_indicators.append(store)
    if args.verbose:
        print(f'Done [{len(places_with_indicators)} w/ indicators] [{len(places_without_indicators)} w/o indicators]')
    
    # Print results
    print(f'Places with possible indicators:', [store.place['name'] for store in places_with_indicators])
    print(f'\nPlaces without possible indicators:', [store.place['name'] for store in places_without_indicators])