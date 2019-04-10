#!/usr/bin/python3
# encoding: utf-8
'''
 -- Web interface for checking darwin core and Nansen legacy files


@author:     Pål Ellingsen
@deffield    updated: Updated
'''


import os
import io
import sys
import cgi
import cgitb
import yaml
import scripts.process_xlsx as px
__updated__ = '2019-03-06'


#cgitb.enable()

method = os.environ.get("REQUEST_METHOD", "GET")

from mako.template import Template
from mako.lookup import TemplateLookup

templates = TemplateLookup(
    directories=['templates'], output_encoding='utf-8')


cores = yaml.load(
    open(os.path.join("config", "config.yaml"), encoding='utf-8'))['cores']

names = []  # For holding a list over the possible setups
for core in cores:
    names.append(core['name'])

# Using sys, as print doesn't work for cgi in python3
template = templates.get_template("check.html")

sys.stdout.flush()
sys.stdout.buffer.write(b"Content-Type: text/html\n\n")

def write_page(names):
    # Write the page
    sys.stdout.buffer.write(
        template.render(names=names))


def warn(message,color='red'):
    message = bytes(message,"utf-8")
    sys.stdout.buffer.write(b'<p style="color:'+bytes(color,"utf-8")+b'">'+message+b'</p>')

if method == "POST":
    
    form = cgi.FieldStorage()

    # For determining what to check against

    setup = form['setup'].value

    sys.stdout.buffer.write(b"<!doctype html>\n<html>\n <meta charset='utf-8'>")
    warn(form['myfile'].filename,color='black')
    # print(form['myfile'].value)
    # warn(form)
    good, error = px.run(io.BytesIO(form['myfile'].value),setup=setup)
    if good:
        warn("File OK :)",color='green')
    else:
        warn("File is not ok :(")
        warn("The following errors were found:")
    for line in error:
        warn(line)
        
    sys.stdout.buffer.write(b'</html>')
elif method == "GET":
    write_page(names)
