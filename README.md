# darwinsheet
Generate DwC spreadsheet templates

Based on code by [umeldt](https://github.com/umeldt) from https://github.com/umeldt/darwinsheet \
The rest is written by [paalge](https://github.com/paalge) (Pål Ellingsen)

This project contains python3 code for generating Darwing core xlsx templates in addition to Nansen Legacy templates.
It also contains a check of such a sheet.

The config.yaml file specifies what is required.

The files.py file contains a dictornary that defines stricter limitations on the Darwin Core terms, 
enabling content checking of variables

## Requirements
Webserver with cgi enables
The python3 code requires:
* numpy
* pandas
* rdflib
* xlrd
* xlsxwriter>=1.0.6
* yaml

## Running
To run the code, the top folder needs to be put in the cgi folder on your webserver.


  
