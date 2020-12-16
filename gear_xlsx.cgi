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
import io

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

    form = cgi.FieldStorage()
   
    print("Content-Type: application/vnd.ms-excel")
    print("Content-Disposition: attachment; filename=Master_Gear_Log.xlsx\n")
    
    path = "/tmp/" + next(tempfile._get_candidate_names()) + '.xlsx'
    
    #Pull data from IMR API in json format. IP address should match IMR API host.
    url = "http://158.39.47.78/api/activities/inCurrentCruise?format=json"
    response = requests.get(url)
    json_activities = response.json()
    
    url = "http://158.39.47.78/api/cruises/current?format=json"
    response = requests.get(url)
    json_cruise = response.json()
    
    data = tl.json_to_df(json_activities,json_cruise)
    
    if "editfile" in form:        
        myfilename = form['myfile'].filename
        with open(myfilename, 'wb') as f:
            f.write(form['myfile'].file.read())                
        data = pd.read_excel(myfilename, sheet_name='Data', header=2)
        data = pd.concat([data_old,data],ignore_index=True).drop_duplicates('eventID', keep='first').reset_index(drop=True)

        
    terms = list(data.columns)
    field_dict = mx.make_dict_of_fields()
    metadata = True
    conversions = True # Include metadata sheet and conversions sheet
    mx.write_file(path,terms,field_dict,metadata,conversions,data)

    with open(path, "rb") as f:
        sys.stdout.flush()
        shutil.copyfileobj(f, sys.stdout.buffer)
    