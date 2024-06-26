
# # # # # # # # # # # # # #
# Main pipeline file
# # # # # # # # # # # # # #
# Argsparser allows usages in command line
# -> Designed to be used as a cronjob(s) on a set of zipcodes
# Essentially a wrapper for all the store.py functionallity.
# 
#
#

import argparse
import os
import csv
import sys
import time
import logging
import time
import pandas as pd
# from detect_text import any_text_triggering
# from places import get_places,  get_place_details,  load_zipcodes, get_place_photo
# from streetview import get_streetview_image
from store import Store
from vision import extract_image_text
from web_scraping import search_key_terms

import shutil
from places import get_places
# from vision import extract_image_text
# import files
import sql

start = time.time()

def load_text(path):
    with open(path, 'r') as f:
        data = f.read().split('\n')
    return data

# # # #
# Proivded set set of query parametres (zipcodes, store-types), we make a "type in zip" query 
# to google's API, and get all stores returned.
# # # #
def get_stores(zipcodes: list, store_types: list, images_dir = 'streetview_images', real = False):
    # Type check wrapping, just in case you want to use a single value insteaad of wrapping in list.
    if(type(zipcodes) == str or type(zipcodes) == int):
        zipcodes = [zipcodes]
    if((type(store_types) == str)):
        store_types = [store_types]
    stores = []
    # On a not real (test run), we are only getting the very first zipcode enad store_type as test
    if not real:
        zipcodes = zipcodes[:1]
        store_types = store_types[:1]
    
    output_dir = 'store_info'  # Directory to save store information files

    print("Writing Stores to file....")
    for zipcode in zipcodes:
        print(f"Processing zipcode: {zipcode}")
        for store_type in store_types: # Make queries
            query = f'{store_type}+in+{zipcode}'
            places = get_places(query)
            if places is None:
                print(f"Skipping {store_type} in {zipcode} due to rate limit exceeded.")
                continue
            
            #List of stores that crash the program when trying to collect their streetview image
            stores_to_skip = ["Kroger", "The Little Clinic", "Costco Pharmacy"]

            for place in places:
                store_name = place['name']
                if any(skip_name in store_name for skip_name in stores_to_skip):
                    print(f"Skipping store: {store_name}")
                    continue

                store = Store(place, images_dir)
                store.get_place_details(verbose=args.verbose)
                store.get_streetview_image(verbose=args.verbose)
                store.get_review_image(verbose=args.verbose)
                store.extract_image_text(reviews=args.real, verbose=args.verbose)
                store.trigger_check(trigger_phrases, verbose=args.verbose)
                store.save_info(zipcode, store_type, output_dir)
                stores.append(store)
           
    print("File Complete!")
    return stores 


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    # Functional Arguments, sort of information we'll be using to pull data and identify trigers.
    parser = argparse.ArgumentParser(description='Pipeline produced by Fall 2023 UofL Capstone Team for Tobacco Permits')
    parser.add_argument('-i', '--images_dir', action='store', default='streetview_images', dest = 'images_dir',
                        help='Directory to save Google Streetview Images to.')
    parser.add_argument('-z', '--zip_codes', action='store', default = 'louisville_metro_zipcodes.txt', dest='zip_codes',
                        help='.txt file to read in selected zipcodes to run algorithm for. \nProvide a .txt file with each word on a newline')
    parser.add_argument('-s','--store_types', action = 'store', default= 'store_types.txt', dest = 'store_types',
                        help='Types of stores to be identified using google places.\nProvide a .txt file with each word on a newline')
    parser.add_argument('-t','--trigger_phrases', action = 'store', default= 'trigger_phrases.txt', dest = 'trigger_phrases',
                        help='Words that are algorithm will look for to \"Flag\" a store. \nProvide a .txt file with each word on a newline.')
    # Testing Arguments
    # TO-DO: Change "real" to be a limit
    # Also: Maybe should have made it --test instead with a store_false
    parser.add_argument('-r', '--real', action = 'store_true', dest = 'real',
                        help = 'Run algorithm on entire dataset over just zipcode + store_type')
    parser.add_argument('-v', '--verbose', action = 'store_true', dest = 'verbose',
                        help ='Be verbose (print statements)')
    parser.add_argument('-sql', '--sql', action = 'store_true', dest = 'sql',
                        help ='Store to attached sql databse.')
    # LOGGING NOT IMPLEMENTED
    # See logging library in python
    parser.add_argument('-l', '--logging', action = 'store_true',  dest = 'logging',
                        help ='Log progress data')
    parser.add_argument('-ld', '--log_dir', action = 'store', default = 'logs' , dest='log_dir',
                        help = 'Where to log')
    
    # These two should be depreciated as against TOS
    parser.add_argument('-c', '--cache', action = 'store_true', dest='cache',
                        help = 'Save data into database and filese')
    parser.add_argument('-sd', '--store_dir', action = 'store', default = 'store_data', dest = 'store_dir',
                        help='If caching, where to save store data')
    
    # PULLING ARGS
    args = parser.parse_args()
    images_dir = args.images_dir
    zipcodes = load_text(args.zip_codes)
    store_types = load_text(args.store_types)
    trigger_phrases = load_text(args.trigger_phrases)
    store_sql = args.sql
    store_csv = args.logging
    # Get places for all store types in all zipcodes
    if args.verbose:
        print('Getting places... ', end='')
    print('Full version:', args.real)
    sys.stdout.flush() # print immediately
    
    # NOTE: Current simplistic search method may have overlap (same place appearing multiple times)
    #
    # args.real is store_true, so if set it will run entire data set, otherwise will not.
    stores = get_stores(zipcodes, store_types, images_dir, args.real)
    # Pefrom pipielin on each store
    # 1. Get place details
    # 2. Using place_id, get streetview images
    # 3. From place_details, we have image_id's for the reviews, so grab thoes too
    # 4. Extract images from reviews and streetview. If real, will do both, street_view_images iirc
    #     a. We can als limit review image sizes if a place has a lot of images i guess. See store.py
    # 5. Check triggers. Calculates indivdual triggers asnd then combines to into is_triggering.
    """for store in stores:
        print(f"Streetview image retrieved for {store.place['name']}")
        store.get_place_details(verbose=args.verbose).get_streetview_image(verbose=args.verbose).get_review_image(verbose=args.verbose)
        print(f"Streetview image retrieved for (After) {store.place['name']}")
        store.extract_image_text(reviews=args.real, verbose = args.verbose)
        store.trigger_check(trigger_phrases, verbose=args.verbose)
        # if not args.real:
        #     break"""
    

    
    # Group places with possible indicators and without
    if args.verbose:
        print('Grouping results... ', end='')
    sys.stdout.flush()
    places_with_indicators = []
    places_without_indicators = []
    if store_sql:
        sql.set_up()
    
    store_dicts = []
    for store in stores:
        print(f"Number of stores: {len(stores)}")
        print(f"Store: {store.place['name']}, is_triggering: {store.is_triggering}")
        # Save store info and images
        if args.cache:
            store.save(args.store_dir)
        if store.is_triggering:
            places_with_indicators.append(store)
            logging.info(f"Added store to places_with_indicators: {store.place['name']}")
            # store_to_db does an upsert, inserting if not existing and then updating is so. Here it is making sure we have it in db.
            #     -> See .sql if you'd like to store additional metadata
            # store_flag then updates the flags of the store in table.
            if store_sql:
                if args.verbose:
                    print('Storing to sql... ', end='')
                sql.store_to_db(store)
                sql.store_flag(store)
            if store_csv:
                if args.verbose:
                    print('Storing to csv... ', end='')
                store_dict = {
                    'place': store.place,
                    'flag_text': store.is_triggering,
                    'flag_image': None, #remove this from UI
                    'flag_website': store.trigger_website,
                    'last_update' : None, #remove this from UI
                    'last_flagged' : None, #remove this from UI
                    'flag_street': store.trigger_street,
                    'flag_review_image': store.trigger_review_image,
                    'flag_review': store.trigger_review,
                        }
                store_dicts.append(store_dict)
        else:
            places_without_indicators.append(store)
            logging.info(f"Added store to places_without_indicators: {store.place['name']}")
    print(f'Done [{len(places_with_indicators)} w/ indicators] [{len(places_without_indicators)} w/o indicators]')

    print(f"Number of places with indicators: {len(places_with_indicators)}")
    print("Places with indicators:")
    
    if store_sql:
        sql.query("select * from INIMAM01.stores").to_csv("store_table.csv", index=False) #Makes a CSV for the temp UI. Can be remove once UI can pull from DB.
    if store_csv:
        df = pd.DataFrame(store_dicts)
        df.to_csv("data.csv", index=False)
    
    for place in places_with_indicators:
        print(place.place['name'])

    print(f"Number of places without indicators: {len(places_without_indicators)}")
    print("Places without indicators:")
    for place in places_without_indicators:
        print(place.place['name'])

    # Print results
    print(f'Places with possible indicators:', [store.place['name'] for store in places_with_indicators])
    print(f'\nPlaces without possible indicators:', [store.place['name'] for store in places_without_indicators])

end = time.time()
print("Time of Program: ", end - start)




            
        
