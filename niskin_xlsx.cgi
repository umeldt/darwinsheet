#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed July 21 13:54 2021

Web interface for creating a log of the niskin bottles

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
import scripts.get_niskin_data as niskin
import pandas as pd

cgitb.enable()

__updated__ = '2021-02-15'

cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(directories = ['templates'], output_encoding='utf-8')

if method == "GET": # This is for getting the page

    template = templates.get_template("niskin_xlsx.html")
    sys.stdout.flush()
    sys.stdout.buffer.write(b"Content-Type: text/html\n\n")
    sys.stdout.buffer.write(
        template.render())

if method == "POST":

    #toktlogger = '10.3.32.62' # GO Sars toktlogger
    toktlogger = 'toktlogger-khaakon.hi.no' # KPH toktlogger
    #toktlogger = '172.16.0.167' # VM of toktlogger at UNIS on my laptop"

    form = cgi.FieldStorage()

    print("Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    print("Content-Disposition: attachment; filename=Niskin_Log.xlsx\n")

    path = "/tmp/" + next(tempfile._get_candidate_names()) + '.xlsx'

    data = niskin.get_niskin_data()
    metadata_df = tl.pull_metadata(toktlogger)

    if "editfile" in form: # If a file has been uploaded, take data from that and append new activities to it.
        oldfilename = '/tmp/oldactivitylog.xlsx'
        with open(oldfilename, 'wb') as f:
            f.write(form['myfile'].file.read())
        #xls = pd.ExcelFile(oldfilename)
        data_old = pd.read_excel(oldfilename, sheet_name='Data', header=2)
        data = pd.concat([data_old,data],ignore_index=True).drop_duplicates('eventID', keep='first').reset_index(drop=True)
        data = data.fillna('')
        metadata_df = pd.read_excel(oldfilename, sheet_name='Metadata', usecols="B,C", index_col=0, header=None).transpose()
        metadata_df = metadata_df.reset_index(drop=True)
        metadata_df = metadata_df.fillna('')

    terms = list(data.columns)
    field_dict = mx.make_dict_of_fields()
    metadata = True
    conversions = True # Include metadata sheet and conversions sheet
    mx.write_file(path,terms,field_dict,metadata,conversions,data, metadata_df)

    with open(path, "rb") as f:
        sys.stdout.flush()
        shutil.copyfileobj(f, sys.stdout.buffer)
