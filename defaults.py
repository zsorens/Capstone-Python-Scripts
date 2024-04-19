# File to use when testing
# Essentailly laods the variables for testing as thought we were running in main.py
# do "from defaults import *"
def load_text(path):
    with open(path, 'r') as f:
        data = f.read().split('\n')
    return data
zipcodes = load_text('louisville_metro_zipcodes.txt')
store_types = load_text('store_types.txt')
trigger_phrases = load_text('trigger_phrases.txt')
images_dir = 'streetview_images'