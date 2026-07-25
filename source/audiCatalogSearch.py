#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Tuesday, March 8, 2022, 8:21 AM
# Partly cloudy ⛅️  🌡️+37°F (feels +28°F, 50%) 🌬️↘27mph 🌓
# searching the audible catalog

import sys
import json
import os
import re

from config import MY_URL_STRING, MY_URL_ROOT, WISHLIST_SYMBOL, LIBRARY_SYMBOL, VENV_PYTHON
from audi_fun import *

def errorItem(myTitle, mySubtitle):
    print(json.dumps({"items": [{
        "title": myTitle,
        "subtitle": mySubtitle,
        "arg": "",
        "icon": {"path": "icons/Warning.png"}
    }]}))
    sys.exit(0)


if not os.path.exists(VENV_PYTHON):
    errorItem("🚨 need to setup first! 🚨", "Enter audible:setup in Alfred")


myLog = sys.stdin.read() # getting output of API-based catalog search

json_data = {}
myTotal = 0
try:
    json_data = json.loads(myLog)
    myTotal = json_data['total_results']
except (json.JSONDecodeError, KeyError):
    errorItem("🚨 catalog search failed", (myLog.strip().splitlines() or ["no output from audible-cli"])[-1])


TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)


result = {"items": []}



myCount = 0

if myTotal >0:

    for T in json_data['products']:

        myCount += 1
        myLibrarySymbol = ''
        pic_string = ''
        asinMatch = checkASIN(T['asin'])
        myLibraryString = "↩️ to add to your wish list " + WISHLIST_SYMBOL
        wishlistCode = 1 #will add to wishlist
        finishedString = ''

        myCurrentRecord = json.dumps(T)

        if asinMatch:
            if asinMatch[0] == "wishlist":
                removeString = ", ↩️ to remove"
                wishlistCode = 2 #will remove from wishlist

            else:
                removeString = ''
                wishlistCode = 0 #indifferent

            myLibraryString = "this item is in your " + asinMatch[0] + removeString
            myLibrarySymbol = asinMatch[1]
            pic_string = cachedImagePath(asinMatch[2])

            if asinMatch[3] == 'True': #is finished checkmark
                finishedString = "✅"



        # narrator block
        narrator_block, firstNarratorName, narrator_list = collapseNarrators(T)

        # getting author info and block
        author_block, firstAuthorID, firstAuthorName, author_list = collapseAuthors(T)

        # title description
        if T.get('extended_product_description'):
            myDescription = remove_tags(T['extended_product_description'])
        else:
            myDescription = ''
        result["items"].append({
                    "title": T.get('title', ''),
                    "subtitle": str(myCount) + "/"+ str(myTotal) + author_block+narrator_block + " " +myLibrarySymbol+" "+finishedString,
                    "quicklookurl": pic_string,
                    "variables": {
                        "myDescription": myDescription,
                        "myURL": MY_URL_STRING+T['asin'],
                        "myCurrentRecord": myCurrentRecord,
                        "myCurrentASIN": T['asin'],
                        "wishlistCode": wishlistCode
                    },
            "mods": {


            "ctrl": {
                "valid": 'true',
                "subtitle": myLibraryString,
                "arg": T['asin']
            },
            "shift+cmd": {
                "valid": 'true',
                "subtitle": "Open your library on Audible "+LIBRARY_SYMBOL,
                "arg": "https://www.audible.com/library/titles"
            },

            "ctrl+cmd": {
                "valid": 'true',
                "subtitle": "Open your Wish List on Audible "+ WISHLIST_SYMBOL,
                "arg": "https://www.audible.com/library/wishlist"
            },
            "cmd": {
                "valid": 'true',
                "subtitle": "Search Audible for books by " + firstAuthorName,
                "arg": MY_URL_ROOT + "author/" + firstAuthorID
            },
            "option": {
                "valid": 'true',
                "subtitle": "Search Audible for books narrated by " + firstNarratorName,
                "arg": MY_URL_ROOT + "search?searchNarrator=" + firstNarratorName
            }},
                    "icon": {

                    "path": pic_string
                    },
                    "valid":'TRUE',

                    "arg": T['asin']
                    })


    print (json.dumps(result))


if myTotal == 0:
    result= {"items": [{
        "title": "No matches",
        "subtitle": "Try a different query",
        "arg": "",
        "icon": {
            "path": "icons/Warning.png"
            }
            }]}
    print (json.dumps(result))
