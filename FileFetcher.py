#!/usr/bin/python

import urllib
import os
import Settings
import time


#############################
def fetch_audio(number):
	fetch_to_file(Settings.remote_audio_url(number), Settings.local_audio_filename(number))
	return Settings.local_audio_filename(number)


#############################
def fetch_html(number):
	fetch_to_file(Settings.remote_html_url(number), Settings.local_html_filename(number) )
	return Settings.local_html_filename(number)


#############################
def fetch_xml():
	fetch_to_file(Settings.remote_xml_url(), Settings.local_base_xml_filename() )
	return Settings.local_base_xml_filename()


#####################
# Fetch a URL and save it to a file
#####################
def fetch_to_file(url, filename):

	if os.path.isfile(filename):
		print "We already have " + filename
		return False

	page = fetch_url(url)
	if "not found" in page.lower():
		raise Exception("Page not found while fetching " + url)
	dirname = os.path.dirname(filename)
	if not os.path.isdir(dirname):
		print "Trying to create folder '{0}'".format(dirname)
		os.mkdir(dirname)
	with open(filename, 'w') as out:
		out.write(page)
		print "   Fetched as " + filename
	return True


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
def fetch_pair(number):

	audio_filename = html_filename = None
	try:
		time.sleep(Settings.WAIT_BETWEEN_FETCH)
		if Settings.CACHE_MP3S:
			audio_filename = fetch_audio(number)
		html_filename = fetch_html(number)
	except Exception as e:
		# Something went bang. Clean up
		if audio_filename is not None and os.path.isfile(audio_filename):
			os.unlink(audio_filename)
		if html_filename is not None and os.path.isfile(html_filename):
			os.unlink(html_filename)
		return False
	return True


#######################
#######################
#######################
def update_cache():
	# First, make sure that the base XML file is here
	if not os.path.isfile(Settings.local_base_xml_filename()):
		print "Looks like we need to fetch the XML file"
		fetch_xml()

	# Next, try to get any missing episodes
	for number in Settings.get_missing_episodes():
		if Settings.have_podcast(number):
			print "Looks like we already had podcast #{0}".format(number)
			Settings.remove_missing_episode(number)
		else:
			print "Trying to fetch missing episode #{0}".format(number)
			if fetch_pair(number):
				print "   Got it!"
				Settings.remove_missing_episode(number)
			else:
				print "   Failed again"

	# Now, try getting episodes beyond what we already have
	number = Settings.get_highest_episode() + 1
	missing = []
	while len(missing) < Settings.MAX_CONSECUTIVE_404S:
		if Settings.have_podcast(number):
			print "Looks like we already had podcast #{0}".format(number)
			Settings.set_highest_episode(number)
		else:
			print "Checking to see if episode {0} is there".format(number)
			if fetch_pair(number):
				print "   Got it!"
				Settings.set_highest_episode(number)
				# Did we miss some before this? If so, mark them as missed
				if len(missing) > 0:
					for num in missing:
						Settings.add_missing_episode(num)
			else:
				print "   Not there."
				missing.append(number)
			# Otherwise, try for the next episode
		number += 1
	print "Looks like {0} is the highest episode number, so far.".format(Settings.get_highest_episode())


if __name__ == '__main__':
	update_cache()
