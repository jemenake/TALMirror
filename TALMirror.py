#!/usr/bin/python

import argparse
import XMLBuilder
import FileFetcher

########################################

def main():
	parser = argparse.ArgumentParser(description='Generate podcast.xml file for archived TAL episodes')
	parser.add_argument('-f', dest='fetch', action='store_const', const=True, default=False, help='Fetch any new episodes')
	parser.add_argument('-g', dest='generate', action='store_const', const=True, default=False, help='Generate XML file')
	args = parser.parse_args()
	if not (args.fetch or args.generate):
		print "You need to specify at least one of the operations (fetch or generate)."
		parser.print_help()
		exit(1)

	if args.fetch:
		print "Trying to fetch missing/new podcasts..."
		FileFetcher.update_cache()
	if args.generate:
		print "Generating XML file"
		XMLBuilder.generate_xml()

if __name__ == '__main__':
	main()