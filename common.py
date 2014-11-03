#!/usr/bin/python

import urllib
import hashlib
import sys
import os

DESCRIPTION_URL = "http://www.thisamericanlife.org/radio-archives/episode/"
AUDIO_URL = "http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/"

LOCAL_FILE_CACHE = "cache/"

LOCAL_RSS_FILE = "podcast.xml"

HTTP_ROOT_URL = "http://mulder.cob.calpoly.edu/~jemenake/TALRelay/"

#############################
def remote_audio_url(number):
	return AUDIO_URL + str(number) + ".mp3"

#############################
def remote_html_url(number):
	return DESCRIPTION_URL + str(number)

#############################
def local_audio_filename(number):
	return  LOCAL_FILE_CACHE + str(number) + ".mp3"

#############################
def local_html_filename(number):
	return  LOCAL_FILE_CACHE + str(number) + ".html"

#############################
def local_audio_url(number):
	return HTTP_ROOT_URL + LOCAL_FILE_CACHE + str(number) + ".mp3"

#############################
def local_xml_url():
	return HTTP_ROOT_URL + LOCAL_RSS_FILE

