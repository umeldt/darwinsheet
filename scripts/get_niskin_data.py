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
#import requests

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
        'dataFilename',
        #'seaWaterPracticalSalinity',
        #'seaWaterTemperatureInCelsius'
        ]

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
    
    data = pd.read_csv(btl_files_folder+ctd_file, header=None, skiprows=range(0,279), delim_whitespace=True,names=('bottleNumber',
                                                                                                  1,
                                                                                                  2,
                                                                                                  3,
                                                                                                  4,#'seaWaterPracticalSalinity',
                                                                                                  5,
                                                                                                  6,
                                                                                                  'sampleDepthInMeters',
                                                                                                  8,#'seaWaterTemperatureInCelsius',
                                                                                                  9,
                                                                                                  10,
                                                                                                  11,
                                                                                                  12,
                                                                                                  13,
                                                                                                  14,
                                                                                                  15,
                                                                                                  16,
                                                                                                  17,
                                                                                                  18,
                                                                                                  19))
    data = data.loc[data[19] == '(avg)']
    data.reset_index(inplace=True)
    
    df_ctd['bottleNumber'] = data['bottleNumber']
    #df_ctd['seaWaterPracticalSalinity'] = data['seaWaterPracticalSalinity']
    #df_ctd['seaWaterTemperatureInCelsius'] = data['seaWaterTemperatureInCelsius']
    
    data['eventID'] = ''
    for index, row in data.iterrows():
        id_url = f'File {ctd_file} niskin bottle {row["bottleNumber"]}' 
        eventID = generate_UUID(id_url)
        df_ctd['eventID'].iloc[index] = eventID
        df_ctd['sampleDepthInMeters'].iloc[index] = row['sampleDepthInMeters']

    return df_ctd


def pull_from_toktlogger():
    '''
    Pull data from toktlogger to a dataframe that can be used to generate attributes consistent for each activity.
    '''
    df_tl = tl.json_to_df('toktlogger-khaakon.hi.no')
    
    return df_tl


def pull_global_attributes(df_ctd,ctd_file, df_tl):
    
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
    df_cruise : TYPE
        DESCRIPTION.

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
