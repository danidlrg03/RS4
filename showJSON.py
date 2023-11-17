#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ../ELE610/TATEM/showJSON.py 
#  A simple program to sum up results of a JSON file created by the ABB TATEM-tool
#  on UiS robot Rudolf. An argument giving the JSON file to open and summarize 
#  must be given as input argument.
#
# Karl Skretting, UiS, September 2023

# Example on how to use file:
#   (C:\...\Anaconda3) C:\..\py3> activate py39
#   (py39) C:\..\ELE610\TATEM> python showJSON.py path_and_filename
#   (py39) C:\..\ELE610\TATEM> python showJSON.py C:\TFS\TATEM\datasets\2023-09-06_14-43-55.json
#   (py39) C:\..\ELE610\TATEM> python showJSON.py datasets\2023-09-06_14-43-55.json
#   (py39) C:\..\ELE610\TATEM> python showJSON.py datasets\2023-09-06_14-49-55.json

import sys
import json

def main(fn):
	with open(fn) as user_file: 
		parsed_json = json.load(user_file)
	#
	if isinstance(parsed_json, list):
		print( f"File {fn} contains a list of {len(parsed_json)} elements." )
		num = -1
		numTaError = 0
		numSuccess = 0
		numNotDefined = 0
		numOther = 0
		time0 = parsed_json[0]['eventStart']
		for e in parsed_json:
			num = num + 1
			if isinstance(e, dict):
				eventTime = (e['eventStart'] - time0)/1e6  # us --> s (?)
				print( f"Element {num:3d} is a dict, {e['eventResult'] = :12s}, {eventTime = :7.3f}" )
				#
				if (e['eventResult']=="TaError"):
					numTaError = numTaError + 1
					# perhaps show details
				elif (e['eventResult']=="Success"):
					numSuccess = numSuccess + 1
				elif (e['eventResult']=="NotDefined"):
					numNotDefined = numNotDefined + 1
				else:
					numOther = numOther + 1
		#
		print( f"Sum: {numSuccess} Success, {numTaError} TaError, {numNotDefined} NotDefined, {numOther} Other." )
	else:
		print( f"File {fn} does not contain a json-list, hmmm." )
	#
	return

if __name__ == "__main__":
	main(sys.argv[1])   
