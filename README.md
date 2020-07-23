# Cloak

Cape-privacy wrapper to work directly with files. 

Implemented Cape transformations (https://docs.capeprivacy.com/libraries/cape-python/transformations/) :
- Tokenizer

## Flow:
* End user find a file to deidentify
* End user creates a config file
* Cloak reads in file as dataframe
* Cloak dynamically creates a cape policy and applies
* End user gets cloak policy and deidentified file

## Config files

Config file is a yaml file that describes how to read source file and how to make transformations

The transformations in the cloak config translate to a cape transformation. For example HASH corresponds to the Cape Tokenizer.

* Specify how the file is delimited and if it contains a header
* Specify which column (1st, 2nd, 3rd, etc) needs a transformation. 
* Specify what type of transformation and additional info for the transformation.

~~~yaml
---
File:
  Delimiter: ','
  Header: True

Columns:
  1:
    transform: 
      type: HASH
      length: 10
  3:
      transform: 
        type: HASH
        length: 40
  4:
    transform: 
      type: DATE
