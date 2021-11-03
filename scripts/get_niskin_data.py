#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 08:24:22 2021

@author: lukem
"""

import pandas as pd
import os
import sys
import re
import uuid
import requests

import os.path
aen_config_dir = (os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

sys.path.append(aen_config_dir+'/scripts')
import toktlogger_json_to_df as tl

btl_files_folder = '/home/pal/kph-ctd/' 

columns = [
        'eventID',
        'parentEventID',
        'bottleNumber',
        'sampleDepthInMeters',
        'eventDate',
        'eventTime',
        'decimalLatitude',
        'decimalLongitude',
        'bottomDepthInMeters',
        'sampleType',
        'gearType',
        'eventRemarks',
        'stationName',
        'statID',
        'samplingProtocol',
        'recordedBy',
        'pi_name',
        'pi_institution',
        'pi_email',
        'sampleLocation',
        'dataFilename'
        ]

def get_cruise_number():
    '''
    Getting the cruise number from the toklogger

    Returns
    -------
    cruiseNum: Integer of cruise number

    '''
    
    toktlogger = 'toktlogger-khaakon.hi.no'
    url = "http://"+toktlogger+"/api/cruises/current?format=json"
    response = requests.get(url)
    json_cruise = response.json()
    cruisenum = int(json_cruise['cruiseNumber'])
    return cruisenum

def create_dataframe():
    '''
    Create empty dataframe to append data from each file to

    Returns
    -------
    df : pandas dataframe
    '''
    
    df = pd.DataFrame(columns=columns)
    
    return df

def generate_UUID(id_url):
    '''
    Generates a v5 UUID. This can be repeatedly generated from the same string.

    Parameters
    ----------
    id_url : string, text to be used to generate UUID

    Returns
    -------
    Version 5 UUID, string

    '''
    return str(uuid.uuid5(uuid.NAMESPACE_URL,id_url))

def pull_columns(df_ctd,ctd_file):
    '''
    Pull columns from .btl file to a pandas dataframe
    '''
    # Creating a new temporary file to read from as .btl file needs cleaning to be understood by Pandas.
    # Note that some columns that I am not interested in are still merged together.
    with open(ctd_file, 'r') as f:
        n = 0 # counter of lines in new temporary file
        try:
            os.remove('/tmp/'+ctd_file)
        except OSError:
            pass
        with open('/tmp/'+ctd_file, 'a') as tmpfile:
            for line in f: # Iterate over lines
                if not line.startswith('*') and not line.startswith('#'): # Ignore header rows
                    if 'sdev' not in line and 'Position' not in line:
                        line = line.replace('(avg)','') # Removing (avg) from end of line - not a column value
                        line = re.sub(r"^\s+", "", line) # Removing whitespace at beginning of line
                        if n == 0: # For header line only
                            line = re.sub("\s+", ",", line)
                        line = re.sub("\s\s+" , ",", line)
                        tmpfile.write(line+'\n')
                    n += 1
    
    data = pd.read_csv('/tmp/'+ctd_file, delimiter=',', usecols=['Bottle', 'PrDM'])
    
    df_ctd['bottleNumber'] = data['Bottle']
    df_ctd['sampleDepthInMeters'] = data['PrDM']
    
    cruisenum = get_cruise_number()
    
    data['eventID'] = ''
    for index, row in data.iterrows():
        id_url = f'File {ctd_file} niskin bottle {row["Bottle"]} cruise {cruisenum}' 
        eventID = generate_UUID(id_url)
        df_ctd['eventID'].iloc[index] = eventID
        #df_ctd['sampleDepthInMeters'].iloc[index] = row['sampleDepthInMeters']

    return df_ctd


def pull_from_toktlogger():
    '''
    Pull data from toktlogger to a dataframe that can be used to generate attributes consistent for each activity.
    '''
    df_tl = tl.json_to_df('toktlogger-khaakon.hi.no')
    
    return df_tl


def pull_global_attributes(df_ctd,ctd_file, df_tl):
    '''
    Add global attributes that are constant for each individual .btl file (corresponding to one CTD cast)

    Parameters
    ----------
    df_ctd : pandas dataframe
        Dataframe to be written to niskin log, for a single CTD deployment 
    ctd_file : string
        Name of .btl file
    df_tl : pandas dataframe
        Data from toktlogger

    Returns
    -------
    df_ctd : pandas dataframe
        Dataframe to be written to niskin log, for a single CTD deployment 

    '''
    df_ctd['dataFilename'] = ctd_file
    
    localStationNumber = int(ctd_file.split('.')[0].split('sta')[1])
    #with open(ctd_file, "rt") as f:
    #    for line in f:
    #        print(line)
    
    df_tmp = df_tl.loc[df_tl['statID'] == localStationNumber]
    
    df_ctd['statID'] = localStationNumber
    df_ctd['eventDate'] = df_tmp.loc[df_tmp['gearType'] == 'CTD w/bottles', 'eventDate'].item()
    df_ctd['parentEventID'] = df_tmp.loc[df_tmp['gearType'] == 'CTD w/bottles', 'eventID'].item()
    df_ctd['eventTime'] = df_tmp.loc[df_tmp['gearType'] == 'CTD w/bottles', 'eventTime'].item()
    df_ctd['decimalLatitude'] = df_tmp.loc[df_tmp['gearType'] == 'CTD w/bottles', 'decimalLatitude'].item()
    df_ctd['decimalLongitude'] = df_tmp.loc[df_tmp['gearType'] == 'CTD w/bottles', 'decimalLongitude'].item()
    df_ctd['bottomDepthInMeters'] = df_tmp.loc[df_tmp['gearType'] == 'CTD w/bottles', 'bottomDepthInMeters'].item()
    
    return df_ctd


def get_niskin_data():
    '''
    Read data from Niskin files into a single pandas dataframe
    This dataframe can be used to create a sample log.

    Returns
    -------
    df_cruise : pandas dataframe
        Dataframe to be written to niskin log 

    '''
    df_cruise = create_dataframe()
    df_tl = pull_from_toktlogger()
    
    for ctd_file in sorted(os.listdir(btl_files_folder)):
        if ctd_file.endswith('.btl'):
            df_ctd = create_dataframe()
            df_ctd = pull_columns(df_ctd, ctd_file)
            df_ctd = pull_global_attributes(df_ctd, ctd_file, df_tl)
            df_cruise = df_cruise.append(df_ctd, ignore_index=True)
    
    df_cruise['stationName'] = ''
    df_cruise['sampleLocation'] = 'Water distributed around children of this event'
    df_cruise['eventRemarks'] = ''
    df_cruise['recordedBy'] = ''
    df_cruise['pi_name'] = ''
    df_cruise['pi_institution'] = ''
    df_cruise['pi_email'] = ''
    df_cruise['sampleType'] = 'Niskin Bottle'
    df_cruise['gearType'] = 'Niskin'
    
    return df_cruise


#df_cruise = get_niskin_data()

#df_cruise.to_csv('niskin_test.csv')
