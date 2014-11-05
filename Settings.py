
import atexit
import pickle
import os.path

#########################
# User configuration varaiables
#########################

# Relative to where you run TALMirror from, where should we store the podcast.xml
# file and the cached files?
WEB_ROOT_PATH = "."
# What's the external URL to
WEB_ROOT_URL = "http://joe.emenaker.com/TALMirror/"
# Should we cache the mp3 files (about 99.8% of the space requirements) or
# should we just point the XML file to the ones hosted by TAL?
# THE FALSE OPTION IS UNTESTED!!!!
CACHE_MP3S = True

##########################
# Other variables which the user probably doesn't need to mess with
##########################

# What to call the local XML file we generate (which will be the file that
# your podcast app downloads)
LOCAL_XML_FILE = "podcast.xml"
# Where (relative to the WEB_ROOT_PATH) to store the cached html/mp3 files
CACHE_FOLDER = "cache/"
# Where do we store the "starting" xml file that we get from TAL?
LOCAL_BASE_XML_FILE = "podcast.base.xml"

# Where to find the XML file which describes the podcast (links to cover-art, credits, etc.)
# This will usually contain only the latest few episodes, so we'll replace that list with
# the list of files we have cached.
XML_URL = "http://feeds.thisamericanlife.org/talpodcast?format=xml"
# Where to find the HTML descriptions of the episodes
HTML_URL = "http://www.thisamericanlife.org/radio-archives/episode/"
# Where to find the MP3 files of the episodes
AUDIO_URL = "http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/"
# We *know* there are at least 538 episodes, so far. So, if you we start getting
# a block of 404's before that, don't stop.
KNOWN_EPISODES = 539

# Seconds to wait between each fetch of a html/mp3 pair, so that we don't bother the servers
WAIT_BETWEEN_FETCH = 8
# How many consecutive 404's should we get before we conclude that we're asking for future episodes?
MAX_CONSECUTIVE_404S = 3

LOCAL_PICKLE_FILE = "settings.pickle"

##########################
# Internal vars
##########################

# This is for storing settings regarding *this* mirror, like: what files are we missing? What
#     is the highest episode number we've seen? Etc...
settings = dict()
KEY_MISSING = 'missing'
KEY_HIGHEST = 'highest'
settings[KEY_MISSING] = set()
settings[KEY_HIGHEST] = 0


############################
# Functions for generating paths/urls
############################

# Definition of Terms:
#
# remote url - the full or beginning URL for getting an original xml/mp3/html file
#		Used *internally* by this program for fetching the originals
# local url - the full or beginning URL for getting *our* copy of an xml/mp3/html file
#		Used in the podcast XML file so that the player will know how to fetch our files
# local filename - the local path to *our* copy of an xml/mp3/html file
#		Used *internally* for saving our local copy of an xml/mp3/html file


#############################
def remote_audio_url(number):
	return AUDIO_URL + str(number) + ".mp3"


#############################
def remote_html_url(number):
	return HTML_URL + str(number)


#############################
def remote_xml_url():
	return XML_URL


#############################
def local_audio_filename(number):
	return os.path.join(WEB_ROOT_PATH, CACHE_FOLDER, str(number) + ".mp3")


#############################
def local_html_filename(number):
	return os.path.join(WEB_ROOT_PATH, CACHE_FOLDER, str(number) + ".html")


#############################
def local_audio_url(number):
	return WEB_ROOT_URL + CACHE_FOLDER + str(number) + ".mp3"


#############################
def local_xml_url():
	return WEB_ROOT_URL + LOCAL_XML_FILE


#############################
def local_xml_filename():
	return os.path.join(WEB_ROOT_PATH, LOCAL_XML_FILE)


#############################
def local_base_xml_filename():
	return os.path.join(WEB_ROOT_PATH, LOCAL_BASE_XML_FILE)


#############################
def have_podcast(number):
	return os.path.isfile(local_audio_filename(number)) and os.path.isfile(local_html_filename(number))

############################
# Functions for saving/getting persistent settings
############################

#############################
def get_missing_episodes():
	return settings[KEY_MISSING]


#############################
def add_missing_episode(number):
	settings[KEY_MISSING].add(number)

#############################
def remove_missing_episode(number):
	settings[KEY_MISSING].remove(number)


#############################
def get_highest_episode():
	return settings[KEY_HIGHEST]


#############################
def set_highest_episode(number):
	settings[KEY_HIGHEST] = number

############################
# Functions for loading/saving the pickle file
############################

#############################
def load_settings():
	global settings
	try:
		settings = pickle.load(open(LOCAL_PICKLE_FILE))
	except Exception as e:
		print "Problem loading saved settings. Starting from scratch."

#############################
def save_settings():
	try:
		pickle.dump(settings, open(LOCAL_PICKLE_FILE,'w'))
	except Exception as e:
		print 'Error saving settings to ' + LOCAL_PICKLE_FILE



load_settings()
# Make sure that we get called when the program finishes
atexit.register(save_settings)