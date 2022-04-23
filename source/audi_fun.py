#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Partly cloudy ⛅️  🌡️+47°F (feels +40°F, 42%) 🌬️→12mph 🌖 Tue Apr 19 17:21:34 2022



import sys
import json
import os
import time
import sqlite3
import re
import urllib.request

from config import MY_DATABASE, UPDATE_DAYS,CACHE_FOLDER_IMAGES, WISHLIST_SYMBOL

timeToday = time.time()


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


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

    os.system ("export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH:$PWD/lib/bin;\
        export PYTHONPATH=$PWD/lib;\
            audible library export --format 'json';\
            audible wishlist export --format 'json';\
                python3 rebuild.py")

    
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
    
    if 'authors' in myRecord:  
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
    if 'narrators' in myRecord:  
        firstNarratorName = myRecord['narrators'][0]['name']
        narrator_block = ", narrated by: "+myRecord['narrators'][0]['name']
        narrator_list = myRecord['narrators'][0]['name']
        for xx in myRecord['narrators'][1:]:
            narrator_block += ',' + xx['name']
            narrator_list += ',' + xx['name']
    return narrator_block, firstNarratorName, narrator_list
            
    
        



# adding a record with the minimum information to see this record (the whole wishlist will be updated at the next database refresh)
def addToWishlist(myRecord):
   myDictRecord = eval(r'''myRecord''')
   myDR = json.loads(myDictRecord)
   myAuthors  = collapseAuthors(myDR)[3]
   try:
       pic_string = re.search('https://m.media-amazon.com/images/I/(.+?)._SL500_.jpg', myDR['product_images']['500']).group(1)
   except AttributeError:
       found = '' # apply your error handling

   ICON_PATH = (CACHE_FOLDER_IMAGES+pic_string+".jpg")
    
   if not os.path.exists(ICON_PATH):
       log ("retrieving image" + ICON_PATH)
       urllib.request.urlretrieve(myDR['product_images']['500'], ICON_PATH)
   myNarrators  = collapseNarrators(myDR)[2]
   db = sqlite3.connect(MY_DATABASE)
   cursor = db.cursor()
   count = cursor.execute (""" INSERT INTO "audible_table" VALUES(?,?,?,?,?,?,'wishlist',?,'')""", (myDR['title'],myDR['subtitle'],myAuthors,myDR['product_images']['500'],myDR['asin'],WISHLIST_SYMBOL, myNarrators))
   db.commit()
   cursor.close()
   db.close()


def removeWishList (myRecord):
    
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



