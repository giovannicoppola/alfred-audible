#!/usr/bin/env python3
# -*- coding: utf-8 -*-


### ALFRED-AUDIBLE

#### Saturday, March 5, 2022, 8:37 PM
# Partly cloudy ⛅️  🌡️+35°F (feels +30°F, 69%) 🌬️0mph 🌒


import sqlite3
import json
import sys
from config import MY_DATABASE, MY_URL_STRING, MY_URL_ROOT, LIBRARY_SYMBOL, WISHLIST_SYMBOL, VENV_PYTHON
from audi_fun import *

### INITIALIZING
if not os.path.exists(VENV_PYTHON):

    resultErr= {"items": [{
        "title": "🚨 need to setup first! 🚨",
        "subtitle": "Enter audible:setup in Alfred",
        "arg": "",
        "icon": {
            "path": ""
            }
            }]}
    print (json.dumps(resultErr))
    quit()



myCheck = checkingTime()
if myCheck == 'toBeUpdated':
    quit()


MYINPUT= sys.argv[1] if len(sys.argv) > 1 else ''
MYQUERY= "%" + MYINPUT + "%"

result = {"items": []}


db = sqlite3.connect(MY_DATABASE)
cursor = db.cursor()



try:
    cursor.execute("""SELECT title,subtitle,authors,cover_url, asin, symbol, narrators, is_finished,source
    FROM audible_table
    WHERE authors || title || subtitle LIKE ?;
    """,(MYQUERY,))

    rs = cursor.fetchall()

except sqlite3.OperationalError as err:
    result= {"items": [{
    "title": "Error: " + str(err),
    "subtitle": "Some error",
    "arg": "",
    "icon": {

            "path": "icons/Warning.png"
        }
    }]}
    print (json.dumps(result))
    raise err


if (rs):
    myResLen = str(len (rs))
    countR=1

    for r in rs:

        title = r[0]
        if r[1] and r[1] != "None":
            subtitle = r[1] + " - "
        else:
            subtitle=''

        authors = r[2] if r[2] and r[2] != "None" else ''
        firstAuthor = authors.split(',')[0] if authors else ''

        narrators = r[6] if r[6] and r[6] != "None" else ''
        narratorBlock = " - narrated by: " + narrators if narrators else ''
        firstNarrator = narrators.split(',')[0] if narrators else ''

        if r[7] == 'True': #is finished checkmark
            finishedString = " ✅"
        else:
            finishedString = ""

        if r[8] == 'wishlist': #is in wishlist
            removeWishlistBlock = "↩️ to remove from your wish list"
            wishlistCode = 2 #will remove from wishlist
        else:
            removeWishlistBlock = "this item is in your library " + LIBRARY_SYMBOL
            wishlistCode = 0 #indifferent

        iconPath = cachedImagePath(r[3])

    #### COMPILING OUTPUT
        result["items"].append({
        "title": title,
        "subtitle": str(countR)+"/"+myResLen + " "+ r[5]+subtitle +authors+narratorBlock+finishedString,
        "arg": "",
        "quicklookurl": iconPath,
        "variables": {
                    "myURL": MY_URL_STRING+r[4]

                        },
        "mods": {
            "ctrl": {
                "valid": 'true',
                "subtitle": removeWishlistBlock,

            "variables": {
            "myCurrentASIN": r[4],
            "wishlistCode": wishlistCode

        },
                "arg": r[4]
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
                "subtitle": "Search Audible for books by "+firstAuthor,
                "arg": MY_URL_ROOT + "search?searchAuthor=" +firstAuthor
            },
            "option": {
                "valid": 'true',
                "subtitle": "Search Audible for books narrated by " + firstNarrator ,
                "arg": MY_URL_ROOT + "search?searchNarrator=" + firstNarrator
            }},
        "icon": {

        "path": iconPath
    }


        })
        countR += 1

    print (json.dumps(result))


if MYINPUT and not rs:
    resultErr= {"items": [{
        "title": "No matches",
        "subtitle": "Try a different query",
        "arg": "",
        "icon": {
            "path": "icons/Warning.png"
            }
            }]}
    print (json.dumps(resultErr))
