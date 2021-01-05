#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 09:04:12 2020

Web interface for creating a master gear log xlsx

@author: Luke Marsden
"""

import os
import time
import sys
import cgi
import cgitb
import codecs
import xlsxwriter
import shutil
import textwrap
import requests
import json
import numpy as np
import shutil
from datetime import datetime as dt
import http.cookies as Cookie
import scripts.make_xlsx as mx
import tempfile
import scripts.toktlogger_json_to_df as tl
import pandas as pd

cgitb.enable()

__updated__ = '2020-12-10'

cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(directories = ['templates'], output_encoding='utf-8')

if method == "GET": # This is for getting the page
    
    template = templates.get_template("gear_xlsx.html")
    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
    sys.stdout.buffer.write(
        template.render())

if method == "POST":
    
    #ip = '10.3.32.62' # GO Sars toktlogger
    #ip = '10.3.64.57' # KPH toktlogger
    ip = '158.39.47.78' # VM of toktlogger at UNIS on my laptop"
    
    #Pull data from IMR API in json format. IP address should match IMR API host.
    url = "http://"+ip+"/api/activities/inCurrentCruise?format=json"
    response = requests.get(url)
    json_activities = response.json()
    
    url = "http://"+ip+"/api/cruises/current?format=json"
    response = requests.get(url)
    json_cruise = response.json()
        
    form = cgi.FieldStorage()
   
    if "txtfile" in form: # Dumping the raw json data to a .txt file
    
        print("Content-Type: text/plain")
        print("Content-Disposition: attachment; filename=raw_gear_log.txt\n")
        
        path = "/tmp/" + next(tempfile._get_candidate_names()) + '.txt'
        
        json_out = [json_cruise] + json_activities 
        
        with open(path, 'w') as outfile:
            json.dump(json_out, outfile)
            
    else: # Creating a .xlsx file of the gear log
    
        print("Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        print("Content-Disposition: attachment; filename=Master_Gear_Log.xlsx\n")
        
        path = "/tmp/" + next(tempfile._get_candidate_names()) + '.xlsx'
        
        data = tl.json_to_df(json_activities,json_cruise)
        
        metadata_df = False
        
        if "editfile" in form: # If a file has been uploaded, take data from that and append new activities to it.        
            oldfilename = '/tmp/oldgearlog.xlsx'
            with open(oldfilename, 'wb') as f:
                f.write(form['myfile'].file.read())                
            data_old = pd.read_excel(oldfilename, sheet_name='Data', header=2)
            data_old = data_old.fillna('')
            data = pd.concat([data_old,data],ignore_index=True).drop_duplicates('eventID', keep='first').reset_index(drop=True)
            metadata_df = pd.read_excel(oldfilename, sheet_name='Metadata', usecols="B,C", index_col=0, header=None).transpose())
            metadata_df = metadata_df.reset_index(drop=True)
            
        terms = list(data.columns)
        field_dict = mx.make_dict_of_fields()
        metadata = True
        conversions = True # Include metadata sheet and conversions sheet
        mx.write_file(path,terms,field_dict,metadata,conversions,data, metadata_df)
        
    
    with open(path, "rb") as f:
        sys.stdout.flush()
        shutil.copyfileobj(f, sys.stdout.buffer)
    