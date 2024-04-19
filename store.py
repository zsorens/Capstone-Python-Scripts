
import os
import sys
import shutil
import re
import json
import requests
from requests.exceptions import Timeout
from vision import extract_image_text


from detect_text import any_text_triggering
from places import  get_place_details,  load_zipcodes, get_place_photo
from streetview import get_streetview_image
from web_scraping import search_key_terms
'''
Alright this is abig file
Store is a class originally only used to store Store data (hehe)
It was later expanded with the Great Main.py Refactor to move most functionally into Store itself.
Is it better? Maybe.
'''
class Store:
    def __init__(self, place = None, images_dir = None):
        self.place = place # Google place
        self.photos = None
        
        self.image_path = None
        self.review_images_dir = None
        
        self.image_text = None
        self.image_review_text = None
        
        self.is_triggering = None
        self.trigger_street = None # Streetview + name
        self.trigger_review_image = None # User-submitted images
        self.trigger_review = None # Review Text
        self.trigger_website = None # Webscraping
        
        self.reviews = None
        self.website = None
        self.images_dir = images_dir
    # Shouldn't be running something something google TOS
    def save(self, store_dir='./store_data'):
        # Create dir to save store data
        place_id = self.place['place_id']
        dir_path = os.path.join(store_dir, place_id)
        os.makedirs(dir_path, exist_ok=True)
        # Move image to store path
        old_image_path = self.image_path
        self.image_path = os.path.join(dir_path, os.path.basename(old_image_path))
        shutil.move(old_image_path, self.image_path)
        data = {
            'place': self.place,
            'photos': self.photos,
            'reviews': self.reviews,
            'images': {
                self.image_path: {
                    'image_text': self.image_text
                }
            },
            'is_triggering': self.is_triggering,
            'website': self.website
        }
        # Save place information
        data_path = os.path.join(dir_path, 'data.json')
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=2)
    # # # 
    # Advanced Details
    # Uses default get_place_details values which are [photos, reviews, website]
    def get_place_details(self, verbose = False):
        if verbose:
            print('Retrieving advanced details...', end='')
            sys.stdout.flush()
        details = get_place_details(self.place['place_id'])
        if details is None:
            if verbose:
                print('ERROR: Failed to retrieve details for place', self.place['place_id'], end = '')
                sys.stdout.flush()
        # Cheating: checks if details is None first, if false then it won't run next conditional so we won't get erro
        # Or atleast my version of python - Alvin
        self.photos = details['photos'] if details and 'photos' in details else []
        self.reviews = details['reviews'] if details and 'reviews' in details else []
        self.website = details['website'] if  details and'website' in details else None
        if verbose:
            print('Done')
        return self
    # # #
    # Street View Images
    # images_dir exepcts filepath relative to function to save photos
    def get_streetview_image(self, images_dir = None, verbose = False, timeout = 30):
        if not images_dir: # If we provide null, give the one we created it with.
            images_dir = self.images_dir
        os.makedirs(images_dir, exist_ok=True)  # Create the directory if it doesn't exist
        if verbose:
            print('Getting streetview images... ', end='')
            sys.stdout.flush()
        try:
            image = get_streetview_image(self.place['formatted_address'], timeout=timeout)
        except Timeout:
            if verbose:
                print(f'Timeout occurred while retrieving streetview image for {self.place["name"]}')
            return self

        # Make directory to temporarily store data
        if not os.path.isdir(images_dir): 
            os.mkdir(images_dir)
        image = get_streetview_image(self.place['formatted_address'])

        if image is None:
            if verbose:
                print('ERROR: Unable to retrieve streetview image for {0}'.format(self.place['name']), end='')
        else:
            try:
                image_path = '{dir}/{place_id}.jpg'.format(
                    dir=images_dir,
                    place_id=self.place['place_id'])
                print(f"Saving streetview image to: {image_path}")
                with open(image_path, 'wb') as f:
                    f.write(image)
                print(f"Streetview image saved for {self.place['name']} at {image_path}")
            except IOError as e:
                print(f"Error saving streetview image for {self.place['name']}: {e}")
            except KeyError as e:
                print(f"Error accessing place data for {self.place['name']}: {e}")

            """image_path = '{dir}/{place_id}.jpg'.format(
            dir=images_dir,
            place_id=self.place['place_id'])
            with open(image_path, 'wb') as f:
                f.write(image)"""
        self.image_path = image_path if image else None # Set the image_path if we pulled an image.
        if verbose:
            print('Done')
            sys.stdout.flush()
        return self
    # # #
    # Review Images
    # images_dir exepcts filepath relative to function to save photos

    def get_review_image(self, images_dir=None, verbose=False):
        if not images_dir:
            images_dir = self.images_dir
        if verbose:
            print(f'Getting review images...', end='')
            sys.stdout.flush()
        if not self.photos:
            print(f'No list of photos in store.photos, Skipping')
            self.review_images_dir = None
            return self
        review_images_dir = f"{images_dir}/{self.place['place_id']}"
        os.makedirs(review_images_dir, exist_ok=True)  # Create the directory if it doesn't exist
        self.review_images_dir = review_images_dir
        for i, photo in enumerate(self.photos, start=1):
            image_review = get_place_photo(photo['photo_reference'])
            image_filename = f"review_image_{i}.jpg"
            image_path = os.path.join(review_images_dir, image_filename)
            with open(image_path, 'wb') as f:
                f.write(image_review)
        if verbose:
            print(f'Done')
        return self

    # # # 
    # Extracting image text
    # reviews -> If you don't want to process the reviews as theres a LOT of images
    # limit -> limited number of reviews you read
     
    def extract_image_text(self, reviews=False, review_limit=None, verbose=False):
        if verbose:
            print('Extracting text from images... ', end='')
        sys.stdout.flush()
        if self.image_path:
            try:
                self.image_text = extract_image_text(self.image_path)[1:]
            except Exception as e:
                print(f"Error extracting text from {self.image_path}: {str(e)}")
                self.image_text = ''
        else:
            if verbose:
                print("No image path...", end='')
            self.image_text = ''
        if reviews and self.review_images_dir:
            for root, dirs, files in os.walk(self.review_images_dir):
                for name in files:
                    image_path = os.path.join(root, name)
                    try:
                        review_text = extract_image_text(image_path)[1:]
                        if self.image_review_text:
                            self.image_review_text += " " + " ".join(review_text)
                        else:
                            self.image_review_text = " ".join(review_text)
                    except Exception as e:
                        print(f"Error extracting text from {image_path}: {str(e)}")
                    if review_limit:
                        review_limit -= 1
                        if review_limit <= 0:
                            break
        if verbose:
            print(f'Done')
        return self

    #check triggers for all our variables 
    def trigger_check(self, trigger_phrases, verbose=False):
        if verbose:
            print('Checking if store names or extracted text is triggering...', end='')
            sys.stdout.flush()
        name = self.place['name']
        strings = [name]
        if self.image_text:
            strings += self.image_text
        self.trigger_street = any_text_triggering(strings, trigger_phrases)
        self.trigger_review_image = any_text_triggering(self.image_review_text.split(), trigger_phrases) if self.image_review_text else None
        self.trigger_review = any_text_triggering(sum([x['text'].split() for x in self.reviews], []), trigger_phrases) if self.reviews else None
        self.trigger_website = search_key_terms(self.website, trigger_phrases) if self.website else None
        self.is_triggering = any([self.trigger_street, self.trigger_review_image, self.trigger_review, self.trigger_website])
        if verbose:
            print('Done')
            sys.stdout.flush()
        return self

    def save_info(self, zipcode, store_type, output_dir):
        store_name = self.place['name']
        # Replace invalid characters with underscores
        store_name = re.sub(r'[<>:"/\\|?*]', '_', store_name)
        file_name = f"{store_name}.txt"
        folder_path = os.path.join(output_dir, zipcode, store_type)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, file_name)
        
        with open(file_path, 'w') as file:
            file.write(f"Store Name: {self.place['name']}\n")
            file.write(f"Address: {self.place['formatted_address']}\n")
            file.write(f"Is Triggering: {self.is_triggering}\n")
            file.write(f"Trigger Street: {self.trigger_street}\n")
            file.write(f"Trigger Review Image: {self.trigger_review_image}\n")
            file.write(f"Trigger Review: {self.trigger_review}\n")
            file.write(f"Trigger Website: {self.trigger_website}\n")
    

    # # #
    #  To remove all the images you just saved in the process
    # Somethong something google TOS
    def __del__(self):
        try:
            if self.image_path and os.path.exists(self.image_path):
                os.remove(self.image_path)
            if self.review_images_dir and os.path.exists(self.review_images_dir):
                shutil.rmtree(self.review_images_dir)
        except Exception as e:
            print("Error Deleting:", e) 
    # # #
    # Debug String for print(store0
    def __str__(self):
        return (f"""Store: {self.place['name']},
              len(photos): {len(self.photos) if self.photos else None},
              image_path: {self.image_path},
              image_text: {self.image_text},
              review_images_dir: {self.review_images_dir},
              image_review_text: {self.image_review_text},
              is_triggering: {self.is_triggering},
              trigger_street: {self.trigger_street}, 
              trigger_review_image: {self.trigger_review_image}, 
              trigger_review: {self.trigger_review},
              trigger_website: {self.trigger_website},
              len(reviews): {len(self.reviews)  if self.photos else None},
              website: {self.website},
              image_dir: {self.images_dir}""")

def test_store_save():
    data = {
        "place": {
            "business_status": "OPERATIONAL",
            "formatted_address": "326 Pearl St, New Albany, IN 47150, United States",
            "geometry": {
            "location": {
                "lat": 38.2857122,
                "lng": -85.8227314
            },
            "viewport": {
                "northeast": {
                "lat": 38.28705722989272,
                "lng": -85.82140512010727
                },
                "southwest": {
                "lat": 38.28435757010728,
                "lng": -85.82410477989272
                }
            }
            },
            "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/shopping-71.png",
            "icon_background_color": "#4B96F3",
            "icon_mask_base_uri": "https://maps.gstatic.com/mapfiles/place_api/icons/v2/shopping_pinlet",
            "name": "Kaiser's Tobacco Store",
            "opening_hours": {
            "open_now": True
            },
            "photos": [
            {
                "height": 4160,
                "html_attributions": [
                "<a href=\"https://maps.google.com/maps/contrib/102120929720335365426\">Philip McMahan</a>"
                ],
                "photo_reference": "ATJ83zjkcO2UGCKxnxpn5YERAsvM3Sp7VX7TdgTXg0xYqO0TKRMb8Yhbd5nyfcKWmCh8bY4oQDV1GcWOHGODyo_Ac8bdXQo1Qb8lQexWxoPClXhGStFH07gH-M1NW-5okQa7Kl7NdCq85ZxWB2EJS1bcXQJ3PwBcLK2wIsspgpQTk1tuC9M",
                "width": 2340
            }
            ],
            "place_id": "ChIJ-R0krlhsaYgRnnahJBqBC9M",
            "plus_code": {
            "compound_code": "75PG+7W New Albany, Indiana",
            "global_code": "86CP75PG+7W"
            },
            "rating": 4.8,
            "reference": "ChIJ-R0krlhsaYgRnnahJBqBC9M",
            "types": [
            "store",
            "point_of_interest",
            "establishment"
            ],
            "user_ratings_total": 44
        },
        "photos": [
            {
                "height": 4160,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/102120929720335365426\">Philip McMahan</a>"
                ],
                "photo_reference": "ATJ83zjqgR9MVFpPT_UkT95zx_f3dlUl-biLpoqnDnexSeyXvJoeIlr_F2uMXoNws4uqksUyaoqvaqNqu_En5qBkV_yU9kIE9F--YOmdbTT2oUnPii9hCzEElZeYFfTU8iT_9SK3H_ZEcjEHcCAa5Ogv3GWlbkxOATMIlXFHdaZ-ORLiFTg",
                "width": 2340
            },
            {
                "height": 3264,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/100853034115816024635\">Quiz Chris</a>"
                ],
                "photo_reference": "ATJ83zh0Sn-jt0NzY2Sg4xquS8BFBEc4sOOLQv9AjO_wLqnk2AXYPAaFX3e7Kq-Z5fbtIn0yyYKKbjMy66GVAEOjXbQWNT16da6vkYvXhb_GhgSsYnVlHDO0momsIPLBu0Aqc2cb4UIqIVPj0cBzUntyt_lltTtahnKUIjg5acvkvUjxFyua",
                "width": 4928
            },
            {
                "height": 3264,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/100853034115816024635\">Quiz Chris</a>"
                ],
                "photo_reference": "ATJ83zhryW3D0slqXZdIECxkukYoMYlmAhOTaoXy11qt3iRQeiR8JUwiTcqeUXETOHvz5t8WnU0GiIHv4vrGYX42CEOYDJUIm0yVTXCvkEb6Bmbh9urNsfD2Ak0o4Zdu9XuUxYZ6Si7NAvI31rcdTSoTuiKIslSo5iYBtth8mLX7JmQtZwIB",
                "width": 4928
            },
            {
                "height": 3264,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/100853034115816024635\">Quiz Chris</a>"
                ],
                "photo_reference": "ATJ83zhcYf1xla5RqOP8egFHYAwVyBOaI4VdFG2vGwoVf08EllPuwDOOt7qF10sxgehcw-ommZ1E6wn1BdHQzartCPtuIPsi_DrJiOlhXN4EEr4-vUhBndnQvNYUackb0uyn7N8Fih862chRcVYLcGM8qluMfO_oXWR9sV32sHSbqoOtF7g-",
                "width": 4928
            },
            {
                "height": 3264,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/100853034115816024635\">Quiz Chris</a>"
                ],
                "photo_reference": "ATJ83zhUJvCgqHCqN3jm2nWthFGQGKPUQHkpZydKA6OBAW8CxUHchr3y_IpXXlszwwjCJA_4f6-15XqqUS23NAuJXSrcnxR0engFvZMrGH3MCf9BC-vKT38DO37DXFV8Z_Eo1qTLtOQWG8AOkbCufKcL5p9B2B4Pmk6upN3Lq5oX4efLqc_k",
                "width": 4928
            },
            {
                "height": 3264,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/100853034115816024635\">Quiz Chris</a>"
                ],
                "photo_reference": "ATJ83ziWU_zJjKFfZVABcvLMtu_hF8V5AW1tDNW3J9L1Q25Rri2B-RVwuGpJdvqBVofj1rEJvODzdCjF-9N5GrxAZsw46aSVb-XJJaV-Gu3tSm1T64o_Ii61j8q-AD7auoxuIKR_PsBAsvBCTV-rWx6dql2yM8qIUBsr7UkE8QEgg8TSayCe",
                "width": 4928
            },
            {
                "height": 1944,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/118163124825243938994\">william Deitsch</a>"
                ],
                "photo_reference": "ATJ83zhF7zkX6lj47chkhtlS3JRMb1weqE0aI_NRddPXgSCZBsKxOV13lhlGW5gM1BFv92dkrX0uzhURLjxiuPJdPpgxBa9gNDSyzIpqQE60oDVPIehnEnDLbBpq6ruMwVmstbjokoW2eDkNsAwc_uaZzGs1ZuY_YXWhATJBqp2b-iud1Qs",
                "width": 2592
            },
            {
                "height": 3024,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/108346784946704856632\">allen vanhoosier</a>"
                ],
                "photo_reference": "ATJ83ziVg9BxGTq_8tKv-AP4l0kE-cWPIiisBwZ5e-TS3FIISH4IBIHXbCcXfZukkb7rNVemcwBuYU0-8uEdzG3QcZotFmil2OLKwIkf2ETM6GyZ58xBE9yNBfaKe2MwCpo5UVZpQljEqDGBWTk-I4jRq7gdF8TABYC6kwpoVHnb5oGYoeHz",
                "width": 4032
            },
            {
                "height": 3264,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/100853034115816024635\">Quiz Chris</a>"
                ],
                "photo_reference": "ATJ83ziUkoNfsD8fHLuMT0CMFRcpXI5sR5pX8c71wDU6CYgzwvQHi90bvROHnht4dCf8xMbvIdzKQg4s8SnpL948szaEfLAPNnhmy5H21c0i2zhGyyvN3B0oHLfQHKGsc5uzk-rFoDKIBcaX2pcC87L1JyFT2Zuky_i7QKezZ0LbzSo95a2g",
                "width": 4928
            },
            {
                "height": 3264,
                "html_attributions": [
                    "<a href=\"https://maps.google.com/maps/contrib/100853034115816024635\">Quiz Chris</a>"
                ],
                "photo_reference": "ATJ83zhVPFcddliVmGwsKbl5IenbeApXXx9M9iEBdgZX2oxPebxuztTj1JonZLHhALLU-qcTtcNDh_Vl8M5P-DgXoc-bXJmxxajFneDU1tLweVjxhkpA_woPJCtQPlum8OMdr2x5aFyeydWcXTu-ISjejqJkOuNb29l0PRRi5qjtcAdmBrlx",
                "width": 4928
            }
        ],
        "reviews": [
            {
                "author_name": "Conor Howard",
                "author_url": "https://www.google.com/maps/contrib/105806070019551652828/reviews",
                "language": "en",
                "original_language": "en",
                "profile_photo_url": "https://lh3.googleusercontent.com/a/ACg8ocIh_ONdnJQwOKC5-xtfIjyJkSnjwgcg-kVsJVTDuEnb=s128-c0x00000000-cc-rp-mo",
                "rating": 5,
                "relative_time_description": "a month ago",
                "text": "Friendly and enthusiastic staff! I was told as far as they know, this is the oldest (1832) continuously family owned tobacco shop in the country. Not the largest selection, but some real gems. Worth a visit for an enthusiast to be sure!",
                "time": 1692468955,
                "translated": False
            },
            {
                "author_name": "Jake Allen",
                "author_url": "https://www.google.com/maps/contrib/113073608829851206076/reviews",
                "language": "en",
                "original_language": "en",
                "profile_photo_url": "https://lh3.googleusercontent.com/a/ACg8ocLOnW2kkr8fMbSfl27CAQvGJse9MppyGGuzpJFmmsG-=s128-c0x00000000-cc-rp-mo",
                "rating": 5,
                "relative_time_description": "2 months ago",
                "text": "Awesome historic place,  good quality cigars, nice staff. The guy who works there told us about the history of the place and showed up some cool antiques around the shop. Glad we stopped by. I'll definitely come back next time I'm around",
                "time": 1689973761,
                "translated": False
            },
            {
                "author_name": "Khyla Art",
                "author_url": "https://www.google.com/maps/contrib/110922539878861301622/reviews",
                "language": "en",
                "original_language": "en",
                "profile_photo_url": "https://lh3.googleusercontent.com/a-/ALV-UjWkEU_ef54RScUf9nXZb_Z-KwsxF6Put5QplMMdbi5vP2g=s128-c0x00000000-cc-rp-mo-ba5",
                "rating": 1,
                "relative_time_description": "12 months ago",
                "text": "Fall festival, walked in older guy says how can I help you fellas? There were three black women. I said I'm not a fellow. He says every one is a fella. Wt-\nSmh. You lost these sales.",
                "time": 1665186358,
                "translated": False
            },
            {
                "author_name": "Amy Singleton",
                "author_url": "https://www.google.com/maps/contrib/111598319592208828649/reviews",
                "language": "en",
                "original_language": "en",
                "profile_photo_url": "https://lh3.googleusercontent.com/a-/ALV-UjW5aRPTfxVrZtN2qxUfglffyRkdkzamvyeqNXLaaF98btk=s128-c0x00000000-cc-rp-mo-ba3",
                "rating": 5,
                "relative_time_description": "a year ago",
                "text": "It's been here since 1832. I'm no longer a smoker but it smells amazing. I can remember going here with my grandpa. I'm happy it's still in business.",
                "time": 1634567042,
                "translated": False
            },
            {
                "author_name": "David Podrasky",
                "author_url": "https://www.google.com/maps/contrib/101916850010490792329/reviews",
                "language": "en",
                "original_language": "en",
                "profile_photo_url": "https://lh3.googleusercontent.com/a/ACg8ocJKdAkoOr8RDFZQRs-oDQfhJI2DngEQdMpICj3ucaya=s128-c0x00000000-cc-rp-mo",
                "rating": 5,
                "relative_time_description": "a year ago",
                "text": "Great little piece of history! Thanks for the tour and stories Chip! Hope you enjoy the stogie!",
                "time": 1648322566,
                "translated": False
            }
        ],
        "images": {
            "./store_data\\ChIJ-R0krlhsaYgRnnahJBqBC9M\\ChIJ-R0krlhsaYgRnnahJBqBC9M.jpg": {
                "image_text": [
                    "111\nGoogle\nnel\n531 34618\n50 43\n11110\n\u24b8 Quiz Chris",
                    "111",
                    "Google",
                    "nel",
                    "531",
                    "34618",
                    "50",
                    "43",
                    "11110",
                    "\u24b8",
                    "Quiz",
                    "Chris"
                ]
            }
        },
        "is_triggering": True,
        "website": "https://kaiserwholesale.com/kaisers-tobacco-store"
        }
    place_id = data['place']['place_id']
    dir_path = os.path.join('store_data', place_id)
    store = Store(data['place'])
    store.photos = data['photos']
    store.reviews = data['reviews']
    store.website = data['website']
    # Only one image currently, so this may seem a little non-sensical at the moment
    for image_path, image_text in data['images'].items():
        image_name = os.path.basename(image_path)
        store.image_path = os.path.join('tmp', image_name)
        os.makedirs(os.path.dirname(store.image_path), exist_ok=True)
        with open(store.image_path, 'w') as f:
            f.write('test_image_data')

        store.image_text = image_text

    store.save()
    
    # Check that directory exists
    if not os.path.isdir(dir_path):
        print('Save directory does not exist')
        return False

    # Check that data file exists
    data_path = os.path.join(dir_path, 'data.json')
    if not os.path.isfile(data_path):
        print('Data file does not exist!')
        return False
    
    # Check that image exists at save location
    for image_path in data['images'].keys():
        if not os.path.isfile(image_path):
            print(f'Image "{image_path}" does not exist!')
            return False
    
    # Check that keys in saved data exist
    with open(data_path, 'r') as f:
        saved_data = json.load(f)
    for key in {'place', 'photos', 'reviews', 'images', 'is_triggering', 'website'}:
        if key not in saved_data:
            print(f'Key "{key}" does not exist in saved json data!')
            return False
    


def test():
    test_store_save()


if __name__ == '__main__':
    test()
