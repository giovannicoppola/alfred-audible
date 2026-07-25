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
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from audi_fun import cachedImagePath, fetchImage

from config import CACHE_FOLDER, MY_DATABASE, WISHLIST_JSON_FILE, WISHLIST_SYMBOL, LIBRARY_SYMBOL, LIBRARY_JSON_FILE, VENV_PYTHON

# every column the workflow queries must exist even if an export comes back empty
REQUIRED_COLUMNS = ["title", "subtitle", "authors", "cover_url", "asin",
					"symbol", "source", "narrators", "is_finished"]


def errorOut(myTitle, mySubtitle):
	print(json.dumps({"items": [{
		"title": myTitle,
		"subtitle": mySubtitle,
		"arg": "",
		"icon": {"path": "icons/Warning.png"}
	}]}))
	sys.exit(0)


def exportData():
## export library and wishlist as JSON into the cache folder.
## note: run with cwd=CACHE_FOLDER and no --output flag, because
## `wishlist export --output` is broken in audible-cli 0.3.3
	if not os.path.exists(VENV_PYTHON):
		errorOut("🚨 need to setup first! 🚨", "Enter audible:setup in Alfred")
	for myCmd in ("library", "wishlist"):
		myRun = subprocess.run(
			[VENV_PYTHON, "-m", "audible_cli", myCmd, "export", "--format", "json"],
			cwd=CACHE_FOLDER, capture_output=True, text=True)
		if myRun.returncode != 0:
			myErrTail = (myRun.stderr or "export failed").strip().splitlines()[-1]
			errorOut("🚨 could not export your " + myCmd, myErrTail)


db=sqlite3.connect(MY_DATABASE)

def importing_json(myFile, mySymbol, myTable):

	## reading JSON data in
	with open(myFile, "r") as read_file:
		json_data = json.load(read_file)


	## getting the list of columns (not all the records have the same columns, nor we can assume that for future dicts)
	# thanks to https://www.codeproject.com/Tips/4067936/Load-JSON-File-with-Array-of-Objects-to-SQLite3-On
	column_list = list(REQUIRED_COLUMNS)
	for data in json_data:
		data['symbol'] = mySymbol
		data['source'] = myTable
		if myTable == 'wishlist':
			data['is_finished'] = ''
		for col in data.keys():
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



# retrieving all the missing images (in parallel, failures leave a generic icon)
	select_statement = "SELECT cover_url FROM "+myTable

	c.execute(select_statement)

	rs = c.fetchall()
	with ThreadPoolExecutor(max_workers=8) as pool:
		for rec in rs:
			pool.submit(fetchImage, rec[0], cachedImagePath(rec[0]))



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


exportData()

importing_json (WISHLIST_JSON_FILE,WISHLIST_SYMBOL,'wishlist')
importing_json (LIBRARY_JSON_FILE,LIBRARY_SYMBOL,'library')
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
