#!/usr/bin/python

import urllib
import hashlib
import sys
import os
from bs4 import BeautifulSoup

DESCRIPTION_URL = "http://www.thisamericanlife.org/radio-archives/episode/"
AUDIO_URL = "http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/"

LOCAL_FILE_CACHE = "cache/"

LOCAL_RSS_FILE = "podcast.xml"

LOCAL_PICKLE_FILE = "pickled.pk"


#############################
def fetch_audio(number):
	fetch_to_file( remote_audio_url(number), local_audio_filename(number) )
	return local_audio_filename(number)

#############################
def fetch_html(number):
	fetch_to_file( remote_html_url(number), local_html_filename(number) )
	return local_html_filename(number)

#############################
def remote_audio_url(number):
	return AUDIO_URL + str(number) + ".mp3"

#############################
def local_audio_filename(number):
	return  LOCAL_FILE_CACHE + str(number) + ".mp3"

#############################
def remote_html_url(number):
	return DESCRIPTION_URL + str(number)

#############################
def local_html_filename(number):
	return  LOCAL_FILE_CACHE + str(number) + ".html"

#####################
# Fetch a URL and save it to a file
#####################
def fetch_to_file(url, filename):

	if os.path.isfile(filename):
		print "We already have " + filename
		return False

	try:
		page = fetch_url(url)
		if "not found" in page.lower():
			raise Exception("Page not found while fetching " + url)
		with open(filename, 'w') as out:
			out.write(page)
			print "   Fetched as " + filename
			return True
	except:
		print sys.exc_info()[0]
		print sys.exc_info()[1]
		print sys.exc_info()[2]
		return False
	return False

#####################
# Fetch a URL
#####################
def fetch_url(url):
	url = url.strip()
	print url

	page = urllib.urlopen(url).read()
	return page

#####################
# Fetch pair
#####################
def fetchPair(number):
	try:
		audio_filename = fetch_audio(number)
		html_filename = fetch_html(number)
	except Exception as e:
		# Something went bang. Clean up
		if audio_filename == None and os.path.isfile(audio_filename):
			os.unlink(audio_filename)
		if html_filename == None and os.path.isfile(html_filename):
			os.unlink(html_filename)
		raise e	

#######################
#######################
#######################
def main():
	import time

	fetchPair(1000)
	
#	for i in range(6,539):
#		fetch_audio(i)
#		fetch_html(i)
#		time.sleep(12)
main()	
