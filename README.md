# Cloak

Cape-privacy wrapper to work directly with files. 

Implemented Cape transformations (https://docs.capeprivacy.com/libraries/cape-python/transformations/) :
- Tokenizer

Flow:
* End user find a file to deidentify
* End user creates a config file that describes how to read source file and how to make transformations
* Cloak reads in file as dataframe
* Cloak dynamically creates a cape policy and applies
* End user gets cloak policy and deidentified file
