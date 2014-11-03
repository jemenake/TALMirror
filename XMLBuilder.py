#!/usr/bin/python

from common import *

import argparse
import bs4
from datetime import datetime
import xml.etree.ElementTree as ET
import traceback
import sys
import os
import os.path

#def remote_audio_url(number):
#def local_audio_filename(number):
#def remote_html_url(number):
#def local_html_filename(number):
#def local_audio_url(number):
#def local_xml_url():

from xml.dom import minidom

######################################
def prettify(elem):
	"""Return a pretty-printed XML string for the Element.
	"""
	rough_string = ET.tostring(elem, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="  ")

######################################
# Extract the act descriptions from the HTML. Returns the results as
# a list of dicts. The dictionary keys are 'head' and 'body'. For example:
# [ { 'head' : 'Prologue', 'body' : 'Ira talks' }, { 'head' : 'Act 1', 'body' : ... } ... ]
#
def getActs(soup):
	acts = []
	act_num = 0

	while True:
		found = soup.find(id="act-" + str(act_num))
		if found is None:
			break

		if isinstance(found, bs4.Tag):
			# Remove all of the odd tags that we don't want
			[s.extract() for s in found.findAll('div', attrs={'class' : 'audio-player'}) ]
			[s.extract() for s in found.findAll('span', attrs={'class' : 'tags'}) ]
			[s.extract() for s in found.findAll('ul', attrs={'class' : 'act-contributors'}) ]
			[s.extract() for s in found.findAll('ul', attrs={'class' : 'actions'}) ]

			head = found.find('div', attrs={'class' : 'act-head'}).getText().strip()
			body = found.find('div', attrs={'class' : 'act-body'}).getText().strip()

			act = { 'head' : head, 'body' : body }
			acts.append(act)
			
			act_num += 1
		else:
			raise Exception("getActs() hit on some HTML which wasn't a tag")

	return acts

######################################
# Searches a given beautifulsoup tree for a tag(s) with certain attributes and returns only the non-tag content
######################################
def getRawContent(soup_body, tag, attributes):

	resultset = soup_body.find(tag, attributes)

	if resultset is None:
		raise LookupError("Couldn't find a tag named '{0}' with attributes '{1}'".format(tag,attributes))

	try:
		for i,result in enumerate(resultset):
			if isinstance(result,bs4.NavigableString):
				pass
			elif isinstance(result,bs4.Tag):
				resultset[i] = result.replaceWithChildren()
			else:
				print "Got some strange type"
				resultset[i] = "ERROR"
	
		value = " ".join([unicode(a).strip() for a in resultset])
		return value
	except Exception as e:
		print "Caught exception in getRawContent: {0}".format(e)
		raise LookupError("Problem in getRawContent when searching for tag named '{0}' with attributes '{1}'".format(tag,attributes))

#####################################
def process_episode(number):
	audiofile = local_audio_filename(number)
	htmlfile = local_html_filename(number)

	# Make sure that we have the html file and the mp3 file
	if not os.path.isfile(htmlfile):
		raise Exception("The HTML file for episode {0} is missing".format(number))
	if not os.path.isfile(audiofile):
		raise Exception("The MP3 file for episode {0} is missing".format(number))

	try:
		file_contents = open(htmlfile, 'r').read().decode('utf-8')
		soup = bs4.BeautifulSoup(file_contents)

	except Exception as e:
		print "Problem trying to read {0}".format(htmlfile)
		raise e

	try:
		# Get size of mp3 file
		filesize =  os.path.getsize(audiofile)
	
		content_div = soup.find("div", { "id" : "content" })
		if content_div is None:
			raise LookupError("Couldn't find a div named 'content_div'")

		acts = getActs(soup)
		# Combine all act text into a single string. *Within* a single act, separate the
		# lines by newlines. *Between* acts, separate them by double-newlines
		all_acts_text = '&#xA;\n&#xA;\n'.join( [ '===========================&#xA;\n' + act['head'] + '&#xA;\n' + act['body'] for act in acts ] )
	
		#item = dict()
		item = ET.Element('item')
	
		# title tag
		title = ET.SubElement(item, 'title')
		title.text = getRawContent(content_div, "h1", { "class" : "node-title" })
	
		description = ET.SubElement(item, 'description')
		description.text = getRawContent(content_div, "div", { "class" : "description" }) + '\n' + all_acts_text
	
		# pubDate tag
		# Dates in the html are in the form of "Dec 22, 1995". Parse them to turn them into the RFC format
		datestring =  getRawContent(content_div, "div", { "class" : "date" })
		dateobj = datetime.strptime( datestring, "%b %d, %Y")
		pubDate = ET.SubElement(item, 'pubDate')
		pubDate.text = dateobj.strftime( "%a, %d %b %Y 00:00:00 +0000" )
	
		url = local_audio_url(number)
	
		# link tag	
		link = ET.SubElement(item, 'link')
		link.text = url
	
		# guid tag
		guid = ET.SubElement(item, 'guid')
		guid.text = url

		# enclosure tag (how to actually find the audio clip)	
		enclosure = ET.SubElement(item, 'enclosure')
		enclosure.set('url',url)
		enclosure.set('length',str(filesize))
		enclosure.set('type','audio/mpeg')

		# itunes:summary tag (this shows where the liner-notes or lyrics normally go)	
#		summary = ET.SubElement(item, 'itunes:summary')
#		summary.text = all_acts_text
#		subtitle = ET.SubElement(item, 'itunes:subtitle')
#		subtitle.text = all_acts_text
		
#		resultset = soup.find_all("div", {"class", "act-body"})
#		print "Acts: {0}".format(len(resultset))
	
		return item
	except ValueError as e:
		print "Caught an error when trying to process episode {0}".format(number)
		raise Error("Problem processing episode {0}".format(number))
	
########################################
def generate_xml():
	tree = ET.parse('podcast.base.xml')
	root = tree.getroot()
	channel = root.find('channel')
	#channel = ET.Element('channel')
	
	for number in range(1,539):
#	for number in range(374,375):
#	for number in range(1,539):
		print "Processing " + str(number)
		try:
			item = process_episode(number)
#			test = prettify(item)
	#		test = test.encode("utf-8")
			channel.append(item)
	#		tree.write(sys.stdout)
	#		print "=========================="
	#		print prettify(channel).encode('utf-8')
		except Exception as e:
			print "Something bad happened while processing episode " + str(number)
			print "{0}".format(e)
			print "{0}".format(sys.exc_info()[0])
			print "{0}".format(sys.exc_info()[1])
			traceback.print_tb(sys.exc_info()[2])
	
	#output = prettify(root).encode('utf-8')
	#output = prettify(channel).encode('utf-8')
	
	#with open(LOCAL_RSS_FILE, "w") as f:
	#	f.write(output)
	tree.write(LOCAL_RSS_FILE)

########################################

parser = argparse.ArgumentParser(description='Generate podcast.xml file for archived TAL episodes')
parser.add_argument('-f', dest='fetch', action='store_const', const=True, default=False, help='Fetch any new episodes')
parser.add_argument('-g', dest='generate', action='store_const', const=True, default=False, help='Generate XML file')
args = parser.parse_args()
if not ( args.fetch or args.generate ):
	print "You need to specify at least one of the operations (fetch or generate)."
	parser.print_help()
	exit(1)

if args.fetch:
	pass
if args.generate:
	generate_xml()

