#!/usr/bin/env python3
#
#
# Saturday, March 5, 2022, 4:29 PM
#

import os


WF_BUNDLE = os.getenv('alfred_workflow_bundleid')
WF_FOLDER = os.getenv('alfred_preferences')+ "/workflows/"+os.getenv('alfred_workflow_uid')
WF_LIB_FOLDER = WF_FOLDER+"/lib"

WISHLIST_SYMBOL = os.path.expanduser(os.getenv('WISHLIST_SYMBOL'))
UPDATE_DAYS = os.path.expanduser(os.getenv('UPDATE_DAYS'))
LIBRARY_SYMBOL = os.path.expanduser(os.getenv('LIBRARY_SYMBOL'))
CATALOG_RESULTS = os.path.expanduser(os.getenv('CATALOG_RESULTS'))
CACHE_FOLDER = os.getenv('alfred_workflow_cache')
CACHE_FOLDER_IMAGES = CACHE_FOLDER+"/images/"
MY_DATABASE = CACHE_FOLDER+"/sql_audi.db"

WISHLIST_JSON_FILE = "wishlist.json"
LIBRARY_JSON_FILE = "library.json"
MY_URL_STRING = "https://www.audible.com/pd/"
MY_URL_ROOT = "https://www.audible.com/"


if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)
if not os.path.exists(CACHE_FOLDER_IMAGES):
    os.makedirs(CACHE_FOLDER_IMAGES)

