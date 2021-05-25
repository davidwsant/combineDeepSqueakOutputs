#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from argparse import ArgumentParser, FileType
import re
import json5
import sys
import glob
import os

args = ArgumentParser('./combineDeepSqueakOutputs.py', description='''This program has been designed to take the excel files created by DeepSqueak and
combine them into a single csv file. The calls from the short call network and the calls from the long call network are checked for overlap to ensure
that no call is counted twice. Currently this program is designed to obtain some information about the files from the file names. The file names
(not the folders containing the files) must include the stripe number, the treatment and the cage number, separated by underscores such as
"Str1_EtOH_CageC". This will need to be updated if the excel files do not contain this information in this order for future experiments.
Example usage: ./combineDeepSqueakOutputs.py -c DeepSqueakExperimentsConfig.json -o AIR_and_EtOH''')

args.add_argument(
	'-c',
	'--config_file',
	type=FileType('r'),
	help="""This is a config file in JSON format with the information about the folders containing the excel files from the output.
	Entries in the config file must contain information for the path to the long call files, the path to the short call files, the treatment
	associated with those files and a name for the set. For an example of formatting, see the file DeepSqueakExperimentsConfig.json. Note
	that the name for each entry does not need to be a date, but this format was just chosen for the example dataset.""",
	default=None,
)

args.add_argument(
	'-o',
	'--output_prefix',
	help="""This is the name you would like to use as the prefix to the output files. By default, the output files will be 'Accepted_calls.csv' and
	'Combined_calls.csv' with no prefix.""",
	default=None,
)


def error_message():
	print()
	print("""\tWelcome to combineDeepSequeakOutputs.py. This program has been designed to take the excel files created by DeepSqueak and
	combine them into a single csv file. Example usage: ./combineDeepSqueakOutputs.py -c DeepSqueakExperimentsConfig.json""")
	print()

args = args.parse_args()
if args.config_file == None:
	error_message()
	print("\tNo config file was entered. Please add a config file using the -c option.")
	json_files =glob.glob('*.json')
	if len(json_files) == 0:
		print('\tNo JSON files are in your present working directory.')
	else:
		print('\tJSON files in your present working directory are:')
		for file in json_files:
			print('\t\t'+file)
	print()
	sys.exit(1)

config_file = json5.load(args.config_file)
output_prefix = args.output_prefix

def get_file_info(file_name, files_information_dict, long_or_short, group_name, mstim):
	search_result = re.search(r"(Str\d)_(.+)_(Cage\w)", file_name)
	if not search_result:
		print("No information was obtained for file: "+file_name)
		return files_information_dict
	stripe = search_result.group(1)
	treatment = search_result.group(2)
	cage = search_result.group(3)
	animal = treatment+'_'+cage+'_'+stripe
	if animal not in files_information_dict:
		files_information_dict[animal] = {}
		files_information_dict[animal]['Cage'] = cage
		files_information_dict[animal]['Stripe'] = stripe
		files_information_dict[animal]['Treatment'] = treatment
		files_information_dict[animal]['files'] = {}
	if group_name not in files_information_dict[animal]['files']:
		files_information_dict[animal]['files'][group_name] = {'long_file': None, 'short_file': None, 'MSTIM': mstim}
	if long_or_short == "long":
		files_information_dict[animal]['files'][group_name]['long_file'] = file_name
	elif long_or_short == "short":
		files_information_dict[animal]['files'][group_name]['short_file'] = file_name
	else:
		print("Long or short variable was input incorrectly")
		print('This should be either "long" or "short" but received '+long_or_short)
		# This part of the loop should never fire
		return files_information_dict
	return files_information_dict

files_information = {}
for entry in config_file:
	for group_name in entry:
		long_files = glob.glob(entry[group_name]['long_files_path']+'*xlsx')
		short_files = glob.glob(entry[group_name]['short_files_path']+'*xlsx')
		mstim = entry[group_name]['mstim_treatment']
		for file in long_files:
			files_information = get_file_info(file, files_information, "long", group_name, mstim)
		for file in short_files:
			files_information = get_file_info(file, files_information, "short", group_name, mstim)

# Now all of the information about the files and samples has been obtained
# The next step is to read the excel sheets into pandas, long and short together so that overlap can be checked

combined_df = pd.DataFrame()

for animal in  files_information:
	cage = files_information[animal]['Cage']
	stripe = files_information[animal]['Stripe']
	treatment = files_information[animal]['Treatment']
	for group_name in files_information[animal]['files']:
		mstim = files_information[animal]['files'][group_name]['MSTIM']
		name = animal+'_'+mstim
		long_file = files_information[animal]['files'][group_name]['long_file']
		short_file = files_information[animal]['files'][group_name]['short_file']
		group = treatment+'_'+mstim
		#group_name is what was previously "Date of Treatment"
		if long_file:
			long_df = pd.read_excel(long_file, index_col=0, header=0)
			long_df['Animal'] = animal
			long_df['Treatment'] = treatment
			long_df['Stripe'] = stripe
			long_df['Cage'] = cage
			long_df['Name'] = name
			long_df['Frequency of MSTIM'] = mstim
			long_df['Group Name (Date)'] = group_name
			long_df['Long or Short'] = "Long"
			long_df['Group'] = group
			long_df['Unique'] = True
			combined_df = pd.concat([combined_df, long_df])
		if short_file:
			short_df = pd.read_excel(short_file, index_col=0, header=0)
			short_df['Animal'] = animal
			short_df['Treatment'] = treatment
			short_df['Stripe'] = stripe
			short_df['Cage'] = cage
			short_df['Name'] = name
			short_df['Frequency of MSTIM'] = mstim
			short_df['Group Name (Date)'] = group_name
			short_df['Long or Short'] = "Short"
			short_df['Group'] = group
			if not long_file:
				short_df['Unique'] = True
			else:
				long_tuples = []
				short_unique = []
				for start, stop, accepted in zip(long_df['Begin Time (s)'], long_df['End Time (s)'], long_df['Accepted']):
					if accepted == True:
						long_tuples.append((start, stop))
				for begin, end in zip(short_df['Begin Time (s)'], short_df['End Time (s)']):
					unique = True
					for entry_tuple in long_tuples:
						if begin >= entry_tuple[0] and begin <= entry_tuple[1]:
							unique = False
						if end >= entry_tuple[0] and begin <= entry_tuple[1]:
							unique = False
					short_unique.append(unique)
				short_df['Unique'] = short_unique
			combined_df = pd.concat([combined_df, short_df])

accepted_df = combined_df[((combined_df['Accepted'] == True)& (combined_df['Unique'] == True))]
output_combined_name = "Combined_calls.csv"
output_accepted_name = "Accepted_calls.csv"
if output_prefix:
	output_combined_name = output_prefix+'_combined_calls.csv'
	output_accepted_name = output_prefix+'_accepted_calls.csv'

combined_df.to_csv(output_combined_name)
accepted_df.to_csv(output_accepted_name)
