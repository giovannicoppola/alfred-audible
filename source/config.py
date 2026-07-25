#!/usr/bin/env python3
#
#
# Saturday, March 5, 2022, 4:29 PM
#

import os


WF_BUNDLE = os.getenv('alfred_workflow_bundleid', 'giovanni-audible')

# data folder (local, not synced): holds the audible-cli virtualenv
DATA_FOLDER = os.getenv('alfred_workflow_data') or os.path.expanduser(
    "~/Library/Application Support/Alfred/Workflow Data/" + WF_BUNDLE)
VENV_FOLDER = DATA_FOLDER + "/venv"
VENV_PYTHON = VENV_FOLDER + "/bin/python"

WISHLIST_SYMBOL = os.getenv('WISHLIST_SYMBOL') or '📕'
UPDATE_DAYS = os.getenv('UPDATE_DAYS') or '30'
LIBRARY_SYMBOL = os.getenv('LIBRARY_SYMBOL') or '📗'
CATALOG_RESULTS = os.getenv('CATALOG_RESULTS') or '50'
CACHE_FOLDER = os.getenv('alfred_workflow_cache') or os.path.expanduser(
    "~/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/" + WF_BUNDLE)
CACHE_FOLDER_IMAGES = CACHE_FOLDER + "/images/"
MY_DATABASE = CACHE_FOLDER + "/sql_audi.db"

# exports are written by audible-cli into the cache folder (see rebuild.py)
WISHLIST_JSON_FILE = CACHE_FOLDER + "/wishlist.json"
LIBRARY_JSON_FILE = CACHE_FOLDER + "/library.json"
MY_URL_STRING = "https://www.audible.com/pd/"
MY_URL_ROOT = "https://www.audible.com/"


for _folder in (CACHE_FOLDER, CACHE_FOLDER_IMAGES, DATA_FOLDER):
    if not os.path.exists(_folder):
        os.makedirs(_folder)
