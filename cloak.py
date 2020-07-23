import cape_privacy as cape
import pandas as pd
import yaml
import os
from datetime import datetime

def read_config(yaml_path):
	'''
	Configs take the form of:
		{
		  "File": {
		    "Header": true, 
		    "Delimiter": ","
		  }, 
		  "Columns": {
		    "1": {
		      "transform": {
		        "length": 10, 
		        "type": "HASH"
		      }
		    }, 
		    "3": {
		      "transform": {
		        "length": 40, 
		        "type": "HASH"
		      }
		    }, 
		    "4": {
		      "transform": {
		        "type": "DATE"
		      }
		    }
		  }
		}
	'''
	with open(yaml_path) as file:
		config = yaml.load(file, Loader=yaml.FullLoader)
		
	# end users input columns starting at 1. 
		# Need to decrement all config['Columns'] keys so they truly represent column indices
	keys = [k - 1 for k in list(config['Columns'].keys())]
	config['Columns'] = dict(zip(keys, config['Columns'].values()))
	return config


def read_file(file_path, config):
	
	if config['File']['Header']:
		header = 0 
	else:
		header = None

	df = pd.read_csv(file_path
		,delimiter=config['File']['Delimiter']
		,header=header
		,dtype=str
		#,engine='c'
		)
	return df

def create_policy(config):
	'''
	Dynamically create Cape Policy based on config file

		- Config transform type to Cave Policy transform type:
			- HASH -> Tokenizer
		- modelling policy file from https://github.com/capeprivacy/cape-python/blob/master/examples/tutorials/mask_personal_information.yaml
	
	'''
	# dynamically create the policy from config
	my_policy = {}
	my_policy['label'] = 'auto_generated'
	my_policy['version'] = 1
	my_policy['rules'] = []

	# For each each column,
		# add the column specific entry to policy file
	for column in config['Columns']:

		col_rules = {}
		col_rules['match'] = {'name':column}
		col_rules['actions'] = []

		# set up transformation
		transform_dict = {}
		transform_type = config['Columns'][column]['transform']['type']
		if transform_type == 'HASH':
			transform_dict['type'] = 'tokenizer'
			transform_dict['max_token_len'] = config['Columns'][column]['transform']['length']
			transform_dict['key'] = 'my_secret'
		else:
			# ignore other transformations
			break
		col_rules['actions'].append({'transform' : transform_dict})

		# add column rules 
		my_policy['rules'].append(col_rules)
		
	# save to disk
	save_path = f'auto_{datetime.now().strftime("%m%d%Y_%H%M%S")}.yaml'
	with open(save_path, 'w') as file:
		_ = yaml.dump(my_policy, file)
		
	return save_path

def deidentify(source_path, config_path):

	# read config and source files
	config = read_config(config_path)
	source_df = read_file(source_path,config)

	# Update config so that the Column key values match column names in data frame
		# this is important for creating Cape policies
	indices = list(config['Columns'].keys())
	all_col_names = list(source_df.columns)
	col_names = [all_col_names[idx] for idx in indices]
	config['Columns'] = dict(zip(col_names, list(config['Columns'].values()))) 

	# create new Cave Policy and apply it to source data frame
	policy_path = create_policy(config)
	policy = cape.parse_policy(policy_path)
	new = cape.apply_policy(policy, source_df)

	# save deidentified file
		# save to working dir for now
	filename_noext, extension = os.path.splitext(source_path)
	_, filename = os.path.split(filename_noext)
	print(filename)
	save_path = f'{filename}_nophi{extension}' 
	new.to_csv(save_path
		,sep=config['File']['Delimiter']
		, index = None
		, header=config['File']['Header'])

	print(f'No PHI file: {save_path}')
	print(f'Cave Policy: {policy_path}')

if __name__ == '__main__':

	config_path = 'test_files/config_header.yaml'
	source_path = 'test_files/source_header.csv'
	# config_path = 'test_files/config_noheader.yaml'
	# source_path = 'test_files/source_noheader.csv'
	deidentify(source_path, config_path)