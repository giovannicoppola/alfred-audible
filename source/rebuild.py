#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Script to build/update a sqlite audible database
#
#
# Created on Saturday, March 5, 2022, 4:10 PM



import json
import sqlite3
import os
import urllib.request
import re
from audi_fun import *

from config import CACHE_FOLDER_IMAGES, MY_DATABASE, WISHLIST_JSON_FILE, WISHLIST_SYMBOL, LIBRARY_SYMBOL, LIBRARY_JSON_FILE


db=sqlite3.connect(MY_DATABASE)

def importing_json(myFile, mySymbol, myTable,myImageFolder):

	
		
	## reading JSON data in
	with open(myFile, "r") as read_file:
		json_data = json.load(read_file)

	
	## getting the list of columns (not all the records have the same columns, nor we can assume that for future dicts)
	# thanks to https://www.codeproject.com/Tips/4067936/Load-JSON-File-with-Array-of-Objects-to-SQLite3-On
	column_list = []
	column = []
	for data in json_data:
		data['symbol'] = mySymbol
		data['source'] = myTable
		if myTable == 'wishlist':
			data['is_finished'] = ''
		column = list(data.keys())
		for col in column:
			if col not in column_list:
				column_list.append(col)

	

	value = []
	values = [] 
	for data in json_data:
		for i in column_list:
			value.append(str(dict(data).get(i)))   
		values.append(list(value)) 
		value.clear()
	

	
# queries

	create_query = "create table if not exists " + myTable + " ({0})".format(" text,".join(column_list))
	insert_query = "insert into " + myTable + " ({0}) values (?{1})".format(",".join(column_list), ",?" * (len(column_list)-1))    
	drop_statement = "DROP TABLE IF EXISTS "+ myTable  
# execution	
	c = db.cursor()   
	c.execute(drop_statement)
	c.execute(create_query)
	c.executemany(insert_query , values)
	values.clear()
	db.commit()



# retrieving all the images
	select_statement = "SELECT cover_url FROM "+myTable
	
	c.execute(select_statement)

	rs = c.fetchall()
	myCount = 1
	for rec in rs:
		
		#print (rec[0])

		try:
			pic_string = re.search('https://m.media-amazon.com/images/I/(.+?)._SL500_.jpg', rec[0]).group(1)
		except AttributeError:
			
			found = '' # apply your error handling
		
		ICON_PATH = myImageFolder+pic_string+".jpg"
		if not os.path.exists(ICON_PATH):
			log ("retrieving image" + ICON_PATH)
			urllib.request.urlretrieve(rec[0], ICON_PATH)
		



	c.close()

	
def combining_tables():
	table_statement= """CREATE TABLE audible_table AS 
	SELECT title, subtitle,authors,cover_url, asin, symbol, source,narrators,is_finished FROM wishlist 
	UNION 
	SELECT title, subtitle,authors,cover_url, asin, symbol,source,narrators,is_finished FROM library"""
	c = db.cursor()   
	c.execute("DROP TABLE IF EXISTS audible_table")
	c.execute(table_statement)
	db.commit()
	c.close()


os.system ("audible library export --format 'json'")
os.system ("audible wishlist export --format 'json'")

importing_json (WISHLIST_JSON_FILE,WISHLIST_SYMBOL,'wishlist',CACHE_FOLDER_IMAGES)
importing_json (LIBRARY_JSON_FILE,LIBRARY_SYMBOL,'library',CACHE_FOLDER_IMAGES)
combining_tables ()



result= {"items": [{
    "title": "Done!" ,
    "subtitle": "ready to search now",
    "arg": "",
    "icon": {

            "path": "icons/done.png"
        }
    }]}
print (json.dumps(result))

