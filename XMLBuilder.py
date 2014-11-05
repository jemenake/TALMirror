#!/usr/bin/python

import Settings

import bs4
from datetime import datetime
import xml.etree.ElementTree as ET
import traceback
import sys
import os
import os.path

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
def get_acts(soup):
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
def get_raw_content(soup_body, tag, attributes):
	# TODO: This might be able to be replaced by getText()

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
	audiofile = Settings.local_audio_filename(number)
	htmlfile = Settings.local_html_filename(number)

	# Make sure that we have the html file and (if desired) the mp3 file
	if Settings.CACHE_MP3S and not os.path.isfile(htmlfile):
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
		# TODO: Come up with some way to get the size of the remote files
		filesize = os.path.getsize(audiofile) if Settings.CACHE_MP3S else 28000000
	
		content_div = soup.find("div", {"id" : "content"})
		if content_div is None:
			raise LookupError("Couldn't find a div named 'content_div'")

		acts = get_acts(soup)
		# Combine all act text into a single string. *Within* a single act, separate the
		# lines by newlines. *Between* acts, separate them by double-newlines
#		we might need to stick a '&#xA;' after each \n
		all_acts_text = '\n\n'.join(['===========================\n' + act['head'] + '\n' + act['body'] for act in acts])

		# Start building our item
		item = ET.Element('item')
	
		# title tag
		title = ET.SubElement(item, 'title')
		title.text = get_raw_content(content_div, "h1", {"class" : "node-title"})
	
		description = ET.SubElement(item, 'description')
		description.text = get_raw_content(content_div, "div", {"class" : "description"}) + '\n' + all_acts_text
	
		# pubDate tag
		# Dates in the html are in the form of "Dec 22, 1995". Parse them to turn them into the RFC format
		datestring =  get_raw_content(content_div, "div", {"class" : "date"})
		dateobj = datetime.strptime(datestring, "%b %d, %Y")
		pubDate = ET.SubElement(item, 'pubDate')
		pubDate.text = dateobj.strftime("%a, %d %b %Y 00:00:00 +0000")

		url = Settings.local_audio_url(number) if Settings.CACHE_MP3S else Settings.remote_audio_url(number)
	
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
		raise Exception("Problem processing episode {0}".format(number))
	
########################################
def generate_xml():
	tree = ET.parse(Settings.local_base_xml_filename())
	root = tree.getroot()
	channel = root.find('channel')

	# Alter the title of this podcast to append ' (Cached)'
	title = channel.find('title')
	title.text += ' (Cached)'

	# Remove any existing items from the channel tag in the base XML file
	items = channel.findall("item")
	for item in items:
		channel.remove(item)

	# Now... add every episode we've got
	for number in range(1, Settings.get_highest_episode()+1):
		print "Processing " + str(number)
		try:
			channel.append(process_episode(number))
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
	tree.write(Settings.local_xml_filename())
	print "You can download the mirrored podcast from:"
	print "   " + Settings.local_xml_url()


if __name__ == '__main__':
	generate_xml()
