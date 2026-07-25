#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Partly cloudy ⛅️  🌡️+47°F (feels +40°F, 42%) 🌬️→12mph 🌖 Tue Apr 19 17:21:34 2022



import sys
import json
import os
import time
import sqlite3
import re
import subprocess
import urllib.request

from config import MY_DATABASE, UPDATE_DAYS, CACHE_FOLDER_IMAGES, WISHLIST_SYMBOL

timeToday = time.time()

IMAGE_URL_RE = re.compile(r'https://m\.media-amazon\.com/images/I/(.+?)\._SL500_\.jpg')


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def cachedImagePath(myURL):
## local cache path for a cover image, '' if the URL is missing or unrecognized
    myMatch = IMAGE_URL_RE.search(myURL or '')
    if not myMatch:
        return ''
    return CACHE_FOLDER_IMAGES + myMatch.group(1) + ".jpg"


def fetchImage(myURL, myPath):
## download a cover image into the cache, ignoring failures (icon just stays generic)
    if not myPath or os.path.exists(myPath):
        return
    try:
        with urllib.request.urlopen(myURL, timeout=15) as response, open(myPath, 'wb') as f:
            f.write(response.read())
    except Exception as err:
        log("could not retrieve image %s: %s", myURL, err)


def checkingTime ():
## Checking if the database needs to be built or rebuilt

    if not os.path.exists(MY_DATABASE):
        log ("database missing ... building")
        databaseRebuild()
    else:
        databaseTime= (int(os.path.getmtime(MY_DATABASE)))
        time_elapsed = int((timeToday-databaseTime)/86400)
        log (str(time_elapsed)+" days from last update")
        if time_elapsed >= int(UPDATE_DAYS):
            log ("rebuilding database ⏳...")
            databaseRebuild()
            log ("done 👍")
            return "toBeUpdated"

def databaseRebuild():
# rebuild.py owns the whole export+import sequence
    myScript = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rebuild.py")
    subprocess.run([sys.executable, myScript], stdout=subprocess.DEVNULL)


def checkASIN (myASIN):


    db = sqlite3.connect(MY_DATABASE)
    cursor = db.cursor()

    cursor.execute("""SELECT source, symbol,cover_url, is_finished
    FROM audible_table
    WHERE asin = ?;
    """,(myASIN,))

    rs = cursor.fetchone()

    return rs


#authors block
def collapseAuthors(myRecord):

    author_block = " -"
    firstAuthorID = ''
    firstAuthorName = ''
    author_list = ''

    if myRecord.get('authors'):
        author_block = " - by: "+ myRecord['authors'][0]['name']
        author_list = myRecord['authors'][0]['name']
        if 'asin' in myRecord['authors'][0]:
            firstAuthorID = myRecord['authors'][0]['asin']
            firstAuthorName = myRecord['authors'][0]['name']


        for xx in myRecord['authors'][1:]:
            author_block += ',' + xx['name']
            author_list += ',' + xx['name']


    return author_block, firstAuthorID, firstAuthorName, author_list

# narrator block
def collapseNarrators(myRecord):
    narrator_block = ''
    firstNarratorName = ''
    narrator_list = ''
    if myRecord.get('narrators'):
        firstNarratorName = myRecord['narrators'][0]['name']
        narrator_block = ", narrated by: "+myRecord['narrators'][0]['name']
        narrator_list = myRecord['narrators'][0]['name']
        for xx in myRecord['narrators'][1:]:
            narrator_block += ',' + xx['name']
            narrator_list += ',' + xx['name']
    return narrator_block, firstNarratorName, narrator_list





# adding a record with the minimum information to see this record (the whole wishlist will be updated at the next database refresh)
def addToWishlist(myRecord):
   myDR = json.loads(myRecord)
   myAuthors  = collapseAuthors(myDR)[3]
   myCoverURL = (myDR.get('product_images') or {}).get('500', '')

   ICON_PATH = cachedImagePath(myCoverURL)
   fetchImage(myCoverURL, ICON_PATH)

   myNarrators  = collapseNarrators(myDR)[2]
   db = sqlite3.connect(MY_DATABASE)
   cursor = db.cursor()
   # values are stored as str() to match how rebuild.py imports them (missing -> 'None')
   cursor.execute ("""INSERT INTO "audible_table" (title,subtitle,authors,cover_url,asin,symbol,source,narrators,is_finished)
       VALUES(?,?,?,?,?,?,'wishlist',?,'')""",
       (str(myDR.get('title')), str(myDR.get('subtitle')), myAuthors, myCoverURL,
        myDR.get('asin'), WISHLIST_SYMBOL, myNarrators))
   db.commit()
   cursor.close()
   db.close()


def removeWishList (myRecord):

    sqliteConnection = None
    try:
        sqliteConnection = sqlite3.connect(MY_DATABASE)
        cursor = sqliteConnection.cursor()


        # Deleting single record now
        sql_update_query = """DELETE from audible_table WHERE asin = ?"""
        cursor.execute(sql_update_query, (myRecord,))
        sqliteConnection.commit()
        log("Record deleted successfully ")
        cursor.close()

    except sqlite3.Error as error:
        log("Failed to delete record from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            log("the sqlite connection is closed")
