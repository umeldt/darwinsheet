#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 09:54:15 2020

@author: lukem
"""

import pandas as pd
from datetime import datetime as dt
import numpy as np

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

def date_only(datetime):
    '''
    Reads string of datetime and returns string of only date
    '''
    return dt.strptime(datetime, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')

def time_only(datetime):
    '''
    Reads string of datetime and returns string of only time
    '''
    return dt.strptime(datetime, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%H:%M:%S')

def json_to_df(json_activities, json_cruise):
    '''
    Provide json data relating to activities and cruise that you have read from IMR API
    
    Returns single dataframe that can be included in the gear log
    '''
    json_activities = list(map( lambda x: flattenjson( x, "__" ), json_activities ))

    key_map = {
            'eventID': 'id',
            'gearType': 'activityTypeName',
            'eventDate': 'startTime',
            'eventTime': 'startTime',
            'cruiseNumber': 'json_cruise', # Cruise number is taken from separate JSON data
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
    
    df = pd.DataFrame(columns=key_map.keys())
    
    for idx, activity in enumerate(json_activities):
        
        # Creating dictionary where key is column header and value is value to be written for that column and activity
        dic = {}
            
        for key, val in key_map.items():
                
            if key in ['eventDate', 'end_date', 'start_date']:
                dic[key] = date_only(activity[val])
                
            elif key in ['eventTime', 'end_time', 'start_time']:
                dic[key] = time_only(activity[val])
                
            elif key in ['decimalLatitude','endDecimalLatitude']:
                dic[key] = activity[val][1]
                
            elif key in ['decimalLongitude','endDecimalLongitude']:
                dic[key] = activity[val][0]
                
            elif key in ['bottomDepthInMeters']:
                numFields = len(activity['fields'])
                depths = [] 
                for fld in range(numFields):
                    if type(activity['fields'][fld]['extendedValue']) == dict:
                        if activity['fields'][fld]['extendedValue']['mapping']['nmeaIdentifier'] == 'EKDBS':
                            if type(activity['fields'][fld]['extendedValue']['result']) == float:
                                if 0 < activity['fields'][fld]['extendedValue']['result'] < 1e4: # Returns 0 when depth out of range of instrument. Removing 0s and spikes from data.
                                    depths.append(activity['fields'][fld]['extendedValue']['result'])
                if len(depths) >= 1:
                    dic[key] = np.mean(depths)
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
                    
            elif key == 'cruiseNumber':
                dic[key] = int(json_cruise['cruiseNumber'])
                
            elif val == '':
                dic[key] = ''
            
            else:
                dic[key] = activity[val]
                  
        df = df.append(dic, ignore_index=True)
        
    return df