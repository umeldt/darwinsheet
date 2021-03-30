#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 09:54:15 2020

@author: lukem
"""

import pandas as pd
import datetime
from datetime import datetime as dt
import numpy as np
import requests
from os.path import os

config_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'config'))

def flattenjson( b, delim ):
    '''

    Parameters
    ----------
    b : TYPE: dict
        DESCRIPTION: json dictionary
    delim : TYPE: string
        DESCRIPTION: When dictionary is flattened, child key is appended to the parent key separated by this delimiter.

    Returns
    -------
    val : TYPE: dict
        DESCRIPTION: dictionary with one tier flattened (put on same level as parent)

    '''
    val = {}
    for i in b.keys():
        if isinstance( b[i], dict ):
            get = flattenjson( b[i], delim )
            for j in get.keys():
                val[ i + delim + j ] = get[j]
        else:
            val[i] = b[i]

    return val

def date_only(timestamp):
    '''
    Reads string of timestamp and returns string of only date
    '''
    return dt.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')

def time_only(timestamp):
    '''
    Reads string of timestamp and returns string of only time
    '''
    return dt.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%H:%M:%S')

def json_to_df(toktlogger):
    '''
    Provide IP or DNS of toktlogger to access IMR API
    
    Returns single dataframe that can be included in the gear log
    '''
    
    #Pull data from IMR API in json format. URL should match IMR API host.
    url = "http://"+toktlogger+"/api/activities/inCurrentCruise?format=json"
    response = requests.get(url)
    json_activities = response.json()
    
    json_activities = list(map( lambda x: flattenjson( x, "__" ), json_activities ))

    key_map = {
            'eventID': 'id',
            'description': 'name',
            'gearType': '',
            'eventDate': 'startTime',
            'eventTime': 'startTime',
            'stationName': 'fields',
            'decimalLatitude': 'startPosition__coordinates',
            'decimalLongitude': 'startPosition__coordinates',
            'bottomDepthInMeters': 'fields',
            'statID': 'superstationNumber',
            'sampleDepthInMeters': '',#
            'maximumDepthInMeters': '',# 
            'minimumDepthInMeters': '',#
            'start_date': 'startTime',
            'end_date': 'endTime',
            'end_time': 'endTime',
            'endDecimalLatitude': 'endPosition__coordinates',
            'endDecimalLongitude': 'endPosition__coordinates',
            'eventRemarks': 'comment',
            'samplingProtocol': '',
            'recordedBy': '',
            'pi_name': '',
            'pi_email': '',
            'pi_institution': ''   
            }
    
    gear_df = pd.read_csv(config_dir+'/list_gear_types.csv')
    
    data = pd.DataFrame(columns=key_map.keys())
    
    for idx, activity in enumerate(json_activities):
        
        if type(activity['endTime']) == str and type(activity['endPosition__coordinates'][0]) == float:
            
            
            # Creating dictionary where key is column header and value is value to be written for that column and activity
            dic = {}
            
            for key, val in key_map.items():
                    
                if key in ['eventDate', 'end_date', 'start_date']:
                    dic[key] = dt.strptime(activity[val], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                elif key in ['eventTime', 'end_time', 'start_time']:
                    dic[key] = dt.strptime(activity[val], '%Y-%m-%dT%H:%M:%S.%fZ').time()
                    
                elif key in ['decimalLatitude','endDecimalLatitude']:
                    dic[key] = activity[val][1]
                    
                elif key in ['decimalLongitude','endDecimalLongitude']:
                    dic[key] = activity[val][0]
                    
                elif key in ['bottomDepthInMeters']:
                    
                    # Retrieving start time and end time of activity so it can be used to pull bottom depth between these times

                    start_dt = dt.strptime(activity['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    end_dt = dt.strptime(activity['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    timediff = end_dt - start_dt
                    
                    # Start time and end time are sometimes the same so need to make them different to pull data.
                    if (timediff).seconds < 2:
                        start_dt = end_dt - datetime.timedelta(seconds=2)
                    
                    start_date = start_dt.strftime('%Y-%m-%d')
                    sthh = "{:02d}".format(start_dt.hour)
                    stmm = "{:02d}".format(start_dt.minute)
                    stss = start_dt.strftime('%S.%f')[:-3]
                    end_date = end_dt.strftime('%Y-%m-%d')
                    ethh = "{:02d}".format(end_dt.hour)
                    etmm = "{:02d}".format(end_dt.minute)
                    etss = end_dt.strftime('%S.%f')[:-3]
                    url = "http://"+toktlogger+"/api/instrumentData/inPeriod?after="+start_date+"T"+sthh+"%3A"+stmm+"%3A"+stss+"Z&before="+end_date+"T"+ethh+"%3A"+etmm+"%3A"+etss+"Z&mappingIds=depth&format=json"
                    response = requests.get(url)
                    json_bd = response.json()
                    
                    if len(json_bd) >= 1:
                        bd = []
                        for i, t in enumerate(json_bd):
                            bd.append(t['numericValue'])
                        dic[key] = np.median([bd])
                    else:
                        dic[key] = ''
                    
                elif key == 'stationName':
                    numFields = len(activity['fields'])
                    for fld in range(numFields):
                        if "station" in activity['fields'][fld]['name'].lower():
                            dic[key] = activity['fields'][fld]['value']
                        else:
                            dic[key] = ''
                    if numFields == 0:
                        dic[key] = ''
                
                # Getting gear type from IMR activities list if possible by using the mapping in the list_gear_types.csv file
                elif key == 'gearType':
                    if activity['activityTypeName'] in gear_df['IMR name'].values:
                        dic[key] = gear_df.loc[gear_df['IMR name'] == activity['activityTypeName'], 'Gear type'].item()
                    else:
                        dic[key] = ''
                    
                elif val == '':
                    dic[key] = ''
                
                else:
                    dic[key] = activity[val]
                      
            data = data.append(dic, ignore_index=True)
        
    return data

def pull_metadata(toktlogger):
    
    url = "http://"+toktlogger+"/api/cruises/current?format=json"
    response = requests.get(url)
    json_cruise = response.json()
    
    metadata_dic = {
        'title': [''],
        'abstract': [''],
        'pi_name': [''],
        'pi_email': [''],
        'pi_institution': [''],
        'pi_address': [''],
        'recordedBy': [''],
        'projectID': [''],
        'cruiseNumber': [int(json_cruise['cruiseNumber'])],
        'vesselName': [json_cruise['vesselName']]
        }

    metadata_df = pd.DataFrame.from_dict(metadata_dic)
    
    return metadata_df