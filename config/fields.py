# encoding: utf-8

'''
 -- This file is for defining the possible fields.
Each field is defined as a dictionary which should contain:

    name : short name of field
    disp_name : The displayed name of the field

Optional fields are:

    width : int
            the width of the cell

    long_list: Boolean
            If the list wil exceed the Excel number of fields set this as true

    dwcid : str
            The Darwin core identifier (an url), if this is used the rest of the names should
            follow the Darwin core

    units : str
            The measurement unit of the variable, using the standard in CF
           Examples: 'm', 'm s-1', '

    cf_name : str
             The variable name in the CF standard

    inherit : Boolean
             Is this a variable that can be inherited by children?
             If it is not present its default is False

    inherit_weak : Boolean
             Only used if inherit is true. If set to True values already
             entered in the children will be kept.
             This is useful for instance in the case of multinets where the
             individual nets have different max and min depths.
             If it is not present its default is False

    valid : dict
            a dictionary with definitions of the validation for the cell, as
            per keywords used in Xlsxwriter

    cell_format :  dict
                   a dictionary with definitions of the format for the cell, as
                   per keywords in Xlsxwriter
    
    measurementType: str
            Term to be used for logging this field in a DwCA Measurement or Fact 
            extension. Best practice is to take this from a controlled volcabulary
            that is specified in the associated 'iri' field below
            
    measurementTypeID: str
            International Resource Identifier (IRI) for the corresponding measurement
            type in a controlled volcabulary. Leave blank if measurement type
            has not been taken from a controlled vocabulary.
            
    measurementUnit: str
            Units for the associated measurementType. Best practice is to use SI
            units, and select them from a controlled volcabulary.
            
    measurementUnitID: ,
            International Resource Identifier (IRI) for the corresponding measurement
            unit in a controlled volcabulary. Leave blank if measurement unit
            has not been taken from a controlled vocabulary.


@author:     Pål Ellingsen, Luke Marsden
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import datetime as dt
import sys
import os
import copy
import csv

__date__ = '2018-05-22'
__updated__ = '2021-11-05'

__config_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'config'))
with open(os.path.join(__config_dir, 'list_sample_types.csv'), 'r', encoding='utf-8') as __f:
    __sample_types = [row.split(",")[0] for row in __f]
    __sample_types = __sample_types[2:]

with open(os.path.join(__config_dir, 'list_gear_types.csv'), 'r', encoding='utf-8') as __f:
    __gear_types = [row.split(",")[0] for row in __f]
    __gear_types = __gear_types[2:]
# ==============================================================================
# ID fields
# ==============================================================================


eventID = {'name': 'eventID',
           'disp_name': 'Event ID',
           'width': 38,
           'dwcid': 'http://rs.tdwg.org/dwc/terms/eventID',
           'valid': {
               'validate': 'length',
               'criteria': '==',
               'value': 36,
               'input_title': 'Event ID',
               'input_message': '''Should be a 36 character long UUID including 4 '-'.
Could be read in with a code reader.''',
               'error_title': 'Error',
               'error_message': "Needs to be a 36 characters long UUID including 4 '- '"
           }
           }


parentEventID = {'name': 'parentEventID',
                 'disp_name': 'Parent event UUID',
                 'width': 38,
                 'dwcid': 'http://rs.tdwg.org/dwc/terms/parentEventID',
                 'valid': {
                     'validate': 'length',
                     'criteria': '==',
                     'value': 36,
                     'input_title': 'Parent event UUID',
                     'input_message': '''ID of the sample this subsample was taken from.
Should be a 36 characters long UUID including 4 '-'
Could be read in with a code reader.''',
                     'error_title': 'Error',
                     'error_message': "Needs to be a 36 characters long UUID including 4 '- '"
                 }
                 }


cruiseNumber = {'name': 'cruiseNumber',
                'disp_name': 'Cruise number',
                'inherit': True,
                'valid': {
                    'validate': 'list',
                    'source': ['2018616',
                               '2018791',
                               '2018707',
                               '2018709',
                               '2018710',
                               '2019616',
                               '2019706',
                               '2019710',
                               '2019711',
                               '2020113',
                               '2021604',
                               '2021702',
                               '2021703',
                               '2021704',
                               '2021708',
                               '2021710',
                               '2021713'
                               ],
                    'input_title': 'Cruise Number',
                    'input_message': '''This is the same for one cruise''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid cruise number '
                }
                }

vesselName = {'name': 'vesselName',
                'disp_name': 'Vessel name',
                'inherit': True,
                'valid': {
                    'validate': 'list',
                    'source': ['Kronprins Haakon',
                               'G.O.Sars',
                               'Kristine Bonnevie'
                               ],
                    'input_title': 'Vessel Name',
                    'input_message': '''Name of the vessel''',
                    'error_title': 'Error',
                    'error_message': 'Not a valid vessel name '
                }
                }

statID = {'name': 'statID',
          'disp_name': 'Local Station ID',
          'inherit': True,
          'width': 13,
          'valid': {
              'validate': 'any',
              'input_title': 'Local Station ID',
              'input_message': '''This ID is a running series (per gear) for each samling event and is found in the cruise logger.
'''
          }
          }


stationName = {'name': 'stationName',
               'disp_name': 'Station Name',
               'inherit': True,
               'width': 13,
               'valid': {
                   'validate': 'any',
                   'input_title': 'Station Name',
                   'input_message': '''The name of the station. NLEG..., etc
This is recorded as SS(superstation) in the cruise logger.'''
               }
               }


# ==============================================================================
# Time and date
# ==============================================================================


eventDate = {'name': 'eventDate',
             'disp_name': 'Date',
             'inherit': True,
             'width': 12,
             'dwcid': 'http://rs.tdwg.org/dwc/terms/eventDate',
             'valid': {
                 'validate': 'date',
                 'criteria': 'between',
                 'minimum': dt.date(2000, 1, 1),
                 'maximum': '=TODAY()+2',
                 'input_title': 'Event Date',
                 'input_message': '''Can be from 2000-01-01 to today +2 days.''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid date [2000-01-01, today + 2]'
             },
             'cell_format': {
                 'num_format': 'yyyy-mm-dd'
             }
             }


start_date = copy.deepcopy(eventDate)
start_date['name'] = 'start_date'
start_date['disp_name'] = 'Start Date'
start_date['inherit'] = True
start_date['valid']['input_title'] = 'Start Date'
start_date.pop('dwcid')

middle_date = copy.deepcopy(start_date)
middle_date['name'] = 'middle_date'
middle_date['disp_name'] = 'Middle Date'
middle_date['inherit'] = True
middle_date['valid']['input_title'] = 'Middle Date'
middle_date['valid']['input_message'] = 'Middle date for event, for instance for noting the deepest point of a trawl or net haul\n' + \
    start_date['valid']['input_message']

end_date = copy.deepcopy(start_date)
end_date['name'] = 'end_date'
end_date['disp_name'] = 'End Date'
end_date['inherit'] = True
end_date['valid']['input_title'] = 'End Date'


eventTime = {'name': 'eventTime',
             'disp_name': 'Time (UTC)',
             'inherit': True,
             'width': 13,
             'dwcid': 'http://rs.tdwg.org/dwc/terms/eventTime',
             'valid': {
                 'validate': 'time',
                 'criteria': 'between',
                 'minimum': 0,  # Time in decimal days
                 'maximum': 0.9999999,  # Time in decimal days
                 'input_title': 'Event Time (UTC)',
                 'input_message': '''
The time in UTC
Format is HH:MM
If MM > 59, HH will be HH + 1 ''',
                 'error_title': 'Error',
                 'error_message': 'Not a valid time'
             },
             'cell_format': {
                 'num_format': 'hh:mm'
             }
             }

# start_time = copy.deepcopy(eventTime)
# start_time['name'] = 'start_time'
# start_time['disp_name'] = 'Start time'
# start_time['valid']['input_title'] = 'Extraction start time'
# start_time.pop('dwcid')
middle_time = copy.deepcopy(eventTime)
middle_time['name'] = 'middle_time'
middle_time['disp_name'] = 'Middle Time'
middle_time['inherit'] = True
middle_time['valid']['input_title'] = 'Middle Time'
middle_time['valid']['input_message'] = 'Middle time for event, for instance for noting the deepest point of a trawl or net haul' + \
    eventTime['valid']['input_message']
middle_time.pop('dwcid')

end_time = copy.deepcopy(eventTime)
end_time['name'] = 'end_time'
end_time['disp_name'] = 'End Time'
end_time['inherit'] = True
end_time['valid']['input_title'] = 'End Time'
end_time['valid']['input_message'] = 'End time for event, for instance for use with a trawl or net haul' + \
    eventTime['valid']['input_message']
end_time.pop('dwcid')


# ==============================================================================
# Position
# ==============================================================================

decimalLatitude = {'name': 'decimalLatitude',
                   'disp_name': 'Latitude',
                   'inherit': True,
                   'width': 10,
                   'units': 'degrees_north',
                   'dwcid': 'http://rs.tdwg.org/dwc/terms/decimalLatitude',
                   'valid': {
                       'validate': 'decimal',
                       'criteria': 'between',
                       'minimum': -90,
                       'maximum': 90,
                       'input_title': 'Decimal Latitude',
                       'input_message': '''Latitude in decimal degrees.
Northern hemisphere is positive.
Example: 78.1500''',
                       'error_title': 'Error',
                       'error_message': 'Not in range [-90, 90]'
                   },
                   'cell_format': {
                       'num_format': '0.0000'
                   }
                   }

decimalLongitude = {'name': 'decimalLongitude',
                    'disp_name': 'Longitude',
                    'inherit': True,
                    'width': 11,
                    'units': 'degree_east',
                    'dwcid': 'http://rs.tdwg.org/dwc/terms/decimalLongitude',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': 'between',
                        'minimum': -180,
                        'maximum': 180,
                        'input_title': 'Decimal Longitude',
                        'input_message': '''Longitude in decimal degrees.
East of Greenwich (0) is positive.
Example: 15.0012''',
                        'error_title': 'Error',
                        'error_message': 'Not in range [-180, 180]'
                    },
                    'cell_format': {
                        'num_format': '0.0000'
                    }
                    }

endDecimalLatitude = {'name': 'endDecimalLatitude',
                      'disp_name': 'End Latitude',
                      'inherit': True,
                      'units': 'degrees_north',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': 'between',
                          'minimum': -90,
                          'maximum': 90,
                          'input_title': 'End Decimal Latitude',
                          'input_message': '''Latitude in decimal degrees.
This is for use with for instance trawls and nets.
Northern hemisphere is positive.
Example: 78.1500''',
                          'error_title': 'Error',
                          'error_message': 'Not in range [-90, 90]'
                      },
                      'cell_format': {
                          'num_format': '0.0000'
                      }
                      }

endDecimalLongitude = {'name': 'endDecimalLongitude',
                       'disp_name': 'End Longitude',
                       'inherit': True,
                       'units': 'degree_east',
                       'valid': {
                           'validate': 'decimal',
                           'criteria': 'between',
                           'minimum': -180,
                           'maximum': 180,
                           'input_title': 'End Decimal Longitude',
                           'input_message': '''Longitude in decimal degrees.
This is for use with for instance trawls and nets.
East of Greenwich (0) is positive.
Example: 15.0012''',
                           'error_title': 'Error',
                           'error_message': 'Not in range [-180, 180]'
                       },
                       'cell_format': {
                           'num_format': '0.0000'
                       }
                       }


middleDecimalLatitude = {'name': 'middleDecimalLatitude',
                         'disp_name': 'Middle Latitude',
                         'inherit': True,
                         'units': 'degrees_north',
                         'valid': {
                             'validate': 'decimal',
                             'criteria': 'between',
                             'minimum': -90,
                             'maximum': 90,
                             'input_title': 'Middle Decimal Latitude',
                             'input_message': '''Latitude in decimal degrees.
This is for use with for instance trawls and nets and denotes the depest point.
Northern hemisphere is positive.
Example: 78.1500''',
                             'error_title': 'Error',
                             'error_message': 'Not in range [-90, 90]'
                         },
                         'cell_format': {
                             'num_format': '0.0000'
                         }
                         }

middleDecimalLongitude = {'name': 'middleDecimalLongitude',
                          'disp_name': 'Middle Longitude',
                          'inherit': True,
                          'units': 'degree_east',
                          'valid': {
                              'validate': 'decimal',
                              'criteria': 'between',
                              'minimum': -180,
                              'maximum': 180,
                              'input_title': 'Middle Decimal Longitude',
                              'input_message': '''Longitude in decimal degrees.
This is for use with for instance trawls and nets and denotes the depest point.
East of Greenwich (0) is positive.
Example: 15.0012''',
                              'error_title': 'Error',
                              'error_message': 'Not in range [-180, 180]'
                          },
                          'cell_format': {
                              'num_format': '0.0000'
                          }
                          }
# ==============================================================================
# Ship
# ==============================================================================

shipSpeedInMetersPerSecond = {'name': 'shipSpeedInMetersPerSecond',
                              'disp_name': 'Ship Speed (m/s)',
                              'inherit': True,
                              'units': 'm/s',
                              'measurementType': 'Ship speed',
                              'measurementTypeID': '',
                              'measurementUnit': 'Metres per second',
                              'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UVAA/',
                              'valid': {
                                  'validate': 'decimal',
                                  'criteria': '>=',
                                  'value': 0,
                                  'input_title': 'Ship Speed (m/s)',
                                  'input_message': '''The speed of the ship in meters per second.
Decimal number >=0.''',
                                  'error_title': 'Error',
                                  'error_message': 'Float >= 0'
                              }
                              }

# ==============================================================================
# Depths
# ==============================================================================

bottomDepthInMeters = {'name': 'bottomDepthInMeters',
                       'disp_name': 'Bottom Depth (m)',
                       'inherit': True,
                       'units': 'm',
                       'cf_name': 'sea_floor_depth_below_sea_surface',
                       'measurementType': 'Sea-floor depth (below instantaneous sea level) {bathymetric depth} in the water body by echo sounder',
                       'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P01/current/MBANZZ01/',
                       'measurementUnit': 'Metres',
                       'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULAA/',
                       'valid': {
                           'validate': 'decimal',
                           'criteria': '>=',
                           'value': 0,
                           'input_title': 'Bottom Depth (m)',
                           'input_message': '''Sea floor depth below sea surface.
Bathymetric depth at measurement site.
0 is the surface.''',
                           'error_title': 'Error',
                           'error_message': 'Float >= 0'
                       }
                       }

sampleDepthInMeters = {'name': 'sampleDepthInMeters',
                       'disp_name': 'Sample Depth (m)',
                       'inherit': True,
                       'units': 'm',
                       'valid': {
                           'validate': 'decimal',
                           'criteria': '>=',
                           'value': 0,
                           'input_title': 'Sample Depth (m)',
                           'input_message': '''The sample depth in meters.
0 is the surface.''',
                           'error_title': 'Error',
                           'error_message': 'Float >= 0'
                       }
                       }


maximumDepthInMeters = {'name': 'maximumDepthInMeters',
                        'disp_name': 'Maximum depth(m)',
                        'inherit': True,
                        'inherit_weak': True,
                        'units': 'm',
                        'dwcid': 'http://rs.tdwg.org/dwc/terms/maximumDepthInMeters',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': 'between',
                            'minimum': 0,
                            'maximum': 9999,
                            'input_title': 'Maximum depth in (m)',
                            'input_message': '''The maximum depth in meters.
0 m is the surface.
9999 m is the bottom.''',
                            'error_title': 'Error',
                            'error_message': 'Float[0, 9999]'
                        }
                        }

minimumDepthInMeters = {'name': 'minimumDepthInMeters',
                        'disp_name': 'Minimum depth (m)',
                        'inherit': True,
                        'inherit_weak': True,
                        'width': 22,
                        'units': 'm',
                        'dwcid': 'http://rs.tdwg.org/dwc/terms/minimumDepthInMeters',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': 'between',
                            'minimum': 0,
                            'maximum': 9999,
                            # 'criteria': '<',
                            # 'value': '=INDIRECT(ADDRESS(ROW(),COLUMN()-1))',
                            'input_title': 'Minimum depth in (m)',
                            'input_message': '''The minimum depth in decimal meters.
0 m is the surface.
Needs to be smaller than the maximum depth''',
                            'error_title': 'Error',
                            'error_message': 'Decimal [0, 9999]'
                        }
                        }
# ==== Altitudes ====
altitudeInMeters = {'name': 'altitudeInMeters',
                    'disp_name': 'Altitude (m)',
                    'inherit': True,
                    'units': 'm',
                    'cf_name': 'altitude',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>=',
                        'value': 0,
                        'input_title': 'Altitude (m)',
                        'input_message': '''The sample altitude in meters.
0 m is the surface. Positive upwards''',
                        'error_title': 'Error',
                        'error_message': 'Float >= 0'
                    }
                    }


maximumElevationInMeters = {'name': 'maximumElevationInMeters',
                            'disp_name': 'Maximum elevation(m)',
                            'inherit': True,
                            'inherit_weak': True,
                            'units': 'm',
                            'dwcid': 'http://rs.tdwg.org/dwc/terms/maximumElevationInMeters',
                            'valid': {
                                'validate': 'decimal',
                                'criteria': '>=',
                                'value': 0,
                                'input_title': 'Maximum elevation in (m)',
                                'input_message': '''The maximum elevation (altitude) in meters.
0 m is the surface.''',
                                'error_title': 'Error',
                                'error_message': 'Float >=0'
                            }
                            }

minimumElevationInMeters = {'name': 'minimumElevationInMeters',
                            'disp_name': 'Minimum elevation(m)',
                            'inherit': True,
                            'inherit_weak': True,
                            'units': 'm',
                            'dwcid': 'http://rs.tdwg.org/dwc/terms/minimumElevationInMeters',
                            'valid': {
                                'validate': 'decimal',
                                'criteria': '>=',
                                'value': 0,
                                'input_title': 'Minimum elevation in (m)',
                                'input_message': '''The minimum elevation (altitude) in meters.
0 m is the surface. Needs to be smaller than the maximum elevation.''',
                                'error_title': 'Error',
                                'error_message': 'Float >=0'
                            }
                            }

# PALEO
sedimentCoreLengthInMeters = {'name': 'sedimentCoreLengthInMeters',
                              'disp_name': 'Sediment Core Length (m)',
                              'units': 'm',
                              'measurementType': 'Sediment core length',
                              'measurementTypeID': '',
                              'measurementUnit': 'Metres',
                              'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULAA/',
                              'valid': {
                                  'validate': 'decimal',
                                  'criteria': '>=',
                                  'value': 0,
                                  'input_title': 'Sediment Core Length (m)',
                                  'input_message': '''The total sediment core length decimal in meters.''',
                                  'error_title': 'Error',
                                  'error_message': 'Float >= 0'
                              }
                              }


sedimentCoreMaximumDepthInCentiMeters = {'name': 'sedimentCoreMaximumDepthInCentiMeters',
                                         'disp_name': 'Sediment Core Maximum Depth (cm)',
                                         'units': 'cm',
                                         'measurementType': 'Sediment core maximum depth',
                                         'measurementTypeID': '',
                                         'measurementUnit': 'Centimetres',
                                         'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                                         'valid': {
                                             'validate': 'decimal',
                                             'criteria': 'between',
                                             'minimum': 0,
                                             'maximum': 3000,
                                             'input_title': 'Sediment Core Maximum Depth (cm)',
                                             'input_message': '''The sediment core maximum depth in centimeters.
This is measured from the top of the core.
Maximum for multicores is 60 cm
Maximum for gravity and piston cores is 3 000 cm.''',
                                             'error_title': 'Error',
                                             'error_message': 'Float[0, 3 000]'
                                         }
                                         }


sedimentCoreMinimumDepthInCentiMeters = {'name': 'sedimentCoreMinimumDepthInCentiMeters',
                                         'disp_name': 'Sediment Core Minimum Depth (cm)',
                                         'units': 'cm',
                                         'measurementType': 'Sediment core minimum depth',
                                         'measurementTypeID': '',
                                         'measurementUnit': 'Centimetres',
                                         'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                                         'valid': {
                                             'validate': 'decimal',
                                             'criteria': 'between',
                                             'minimum': 0,
                                             'maximum': 3000,
                                             'input_title': 'Sediment Core Minimum Depth (m)',
                                             'input_message': '''The sediment core minimum depth in centimeters.
This is measured from the top of the core.''',
                                             'error_title': 'Error',
                                             'error_message': 'Float[0, 3 000]'
                                         }
                                         }
# ==============================================================================
# String parameters
# LABEL: Strings
# ==============================================================================

# Method for making a new string property


def make_string_dict(name):
    return {'name': name,
            'disp_name': name.title().replace('_', ' '),
            'valid': {
                'validate': 'any',
                'input_title': name.title().replace('_', ' '),
                'input_message': name.title().replace('_', ' ')
            }
            }


colour = make_string_dict('colour')
smell = make_string_dict('smell')
description = make_string_dict('description')

eventRemarks = {'name': 'eventRemarks',
                'disp_name': 'Event Remarks',
                'width': 40,
                'dwcid': 'http://rs.tdwg.org/dwc/terms/eventRemarks',
                'valid': {
                         'validate': 'any',
                         'input_title': 'Event Remarks',
                         'input_message': 'Comments about the Event.'
                }
                }

fieldNotes = {'name': 'fieldNotes',
              'disp_name': 'Field Notes',
              'width': 40,
              'dwcid': 'http://rs.tdwg.org/dwc/terms/fieldNotes',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Field Remarks',
                  'input_message': 'Notes from the field.'
              }
              }

occurrenceRemarks = {'name': 'occurrenceRemarks',
                     'disp_name': 'Occurrence Remarks',
                     'width': 40,
                     'dwcid': 'http://rs.tdwg.org/dwc/terms/occurrenceRemarks',
                     'valid': {
                         'validate': 'any',
                         'input_title': 'Occurrence Remarks',
                         'input_message': 'Comments or notes about the Occurrence.'
                     }
                     }

recordedBy = {'name': 'recordedBy',
              'disp_name': 'Recorded By',
              'dwcid': 'http://rs.tdwg.org/dwc/terms/recordedBy',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Recorded By',
                  'input_message': '''Who has recorded/analysed the data.
Can be a concatenated list, separated by: ';'
Example: John Doe; Ola Nordmann'''
              }
              }

recordNumber = {'name': 'recordNumber',
                'disp_name': 'Record Number',
                'dwcid': 'http://rs.tdwg.org/dwc/terms/recordNumber',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Recorded Number',
                    'input_message': '''This is an additional number used to identify the sample.
This is in addition to the event ID'''
                }
                }

individualCount = {'name': 'individualCount',
                   'disp_name': 'Individual Count',
                   'width': 20,
                   'units': '1',
                   'dwcid': 'http://rs.tdwg.org/dwc/terms/individualCount',
                   'valid': {
                       'validate': 'integer',
                       'criteria': '>',
                       'value': 0,
                       'input_title': 'Abundance',
                       'input_message': '''Integer > 0''',
                       'error_title': 'Error',
                       'error_message': 'Integer > 0'
                   }
                   }


storageTemp = {'name': 'storageTemp',
               'disp_name': 'Storage temp',
               'width': 15,
               #'measurementType': '',
               #'measurementTypeID': '',
               #'measurementUnit': 'Degrees Celsius',
               #'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPAA/',
               'valid': {
                   'validate': 'list',
                   'source': [
                       'neg 196 C (LN)',
                       'neg 80 C',
                       'neg 20 C',
                       'Cool room',
                       'Room temp'],
                   'input_title': 'Storage temperature',
                   'input_message': '''Choose the necessary storage temperature''',
                   'error_title': 'Error',
                   'error_message': 'Not a valid storage temperature'
               }
               }

incubationTemperatureInCelsius = {'name': 'incubationTemperatureInCelsius',
        'disp_name': 'Incubation Temperature (C)',
        'units': 'Celsius',
        'measurementType': 'Incubation temperature',
        'measurementTypeID': '',
        'measurementUnit': 'Degrees Celsius',
        'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPAA/',
        'valid': {
            'validate': 'decimal',
            'criteria': '>',
            'value': -10,
            'input_title': 'Incubation Temperature(C)',
            'input_message': '''Temperature at which the experiment is run
 Float number larger than -10 ''',
 'error_title': 'Error',
 'error:message': 'Float > -10'
 }
        }

fixative = {'name': 'fixative',
        'disp_name': 'Fixative',
        'measurementType': 'Fixative',
        'measurementTypeID': '',
        'measurementUnit': 'NA',
        'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
            'valid': {
                'validate': 'any',
                'input_title': 'Fixative',
                'input_message': '''Fixative used for sample '''
            }
            }

bottleNumber = {'name': 'bottleNumber',
                'disp_name': 'Bottle Number',
                'inherit': True,
                'valid': {
                    'validate': 'integer',
                    'criteria': '>',
                    'value': 0,
                    'input_title': 'Bottle Number',
                    'input_message': '''The bottle number
Could be for instance the niskin bottle number.
Positive integer''',
                    'error_title': 'Error',
                    'error_message': 'Integer > 0'
                }
                }

sampleLocation = {'name': 'sampleLocation',
                  'disp_name': 'Sample Location',
                  'valid': {
                      'validate': 'any',
                      'input_title': 'Sample Location',
                      'input_message': '''The storage location on shore.
This could for instance be an institution or something more specific'''
                  }
                  }

dilution_factor = {'name': 'dilution_factor',
                   'disp_name': 'Dilution factor',
                   'width': 20,
                   'measurementType': 'Dilution factor',
                   'measurementTypeID': '',
                   'measurementUnit': 'NA',
                   'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
                   'valid': {
                       'validate': 'integer',
                       'criteria': '>',
                       'value': 0,
                       'input_title': 'Dilution factor',
                       'input_message': '''Positive integer''',
                       'error_title': 'Error',
                       'error_message': 'Integer > 0'
                   }
                   }


filter = {'name': 'filter',
          'disp_name': 'Filter',
          'width': 15,
          'valid': {
              'validate': 'list',
              'source': ['None', 'GFF', '10 µm'],
              'input_title': 'Filter',
              'input_message': '''Choose the filter used.
If no filtering is being done choose None''',
              'error_title': 'Error',
              'error_message': 'Not a valid filter'
          }
          }

filteredVolumeInMilliliters = {'name': 'filteredVolumeInMilliliters',
                               'disp_name': 'Filtered volume (mL)',
                               'measurementType': 'Filtered volume',
                               'measurementTypeID': '',
                               'measurementUnit': 'Millilitres',
                               'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/VVML/',
                               'valid': {
                                   'validate': 'decimal',
                                   'criteria': '>',
                                   'value': 0,
                                   'input_title': 'Filtered volume (mL)',
                                   'input_message': '''Filtered volume in decimal millilitres''',
                                   'error_title': 'Error',
                                   'error_message': 'Decimal > 0'
                               }
                               }

methanol_vol = {'name': 'methanol_vol',
                'disp_name': 'Methanol volume (mL)',
                'units': 'mL',
                'measurementType': 'Methanol volume',
                'measurementTypeID': '',
                'measurementUnit': 'Millilitres',
                'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/VVML/',
                'valid': {
                    'validate': 'integer',
                    'criteria': '>',
                    'value': 0,
                    'input_title': 'Methanol volume (mL)',
                    'input_message': '''Methanol volume in integer millilitres''',
                    'error_title': 'Error',
                    'error_message': 'Integer > 0'
                }
                }

sampleVolumeInMilliliters = {'name': 'sampleVolumeInMilliliters',
                             'disp_name': 'Sample volume (mL)',
                             'units': 'mL',
                             'measurementType': 'Sample volume',
                             'measurementTypeID': '',
                             'measurementUnit': 'Millilitres',
                             'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/VVML/',
                             'valid': {
                                 'validate': 'decimal',
                                 'criteria': '>',
                                 'value': 0,
                                 'input_title': 'Sample volume (mL)',
                                 'input_message': '''Sample volume in decimal millilitres''',
                                 'error_title': 'Error',
                                 'error_message': 'Decimal > 0'
                             }
                             }


subsample_vol = {'name': 'subsample_vol',
                 'disp_name': 'Subsample volume (mL)',
                 'units': 'mL',
                 'measurementType': 'Subsample volume',
                 'measurementTypeID': '',
                 'measurementUnit': 'Millilitres',
                 'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/VVML/',
                 'valid': {
                     'validate': 'integer',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Subsample volume (mL)',
                     'input_message': '''Subsample volume in integer millilitres''',
                     'error_title': 'Error',
                     'error_message': 'Integer > 0'
                 }
                 }

subsample_number = {'name': 'subsample_number',
                    'disp_name': 'Number of subsamples',
                    #'measurementType': '',
                    #'measurementTypeID': '',
                    #'measurementUnit': 'NA',
                    #'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
                    'valid': {
                        'validate': 'integer',
                        'criteria': '>',
                        'value': 0,
                        'input_title': 'Integer number of subsamples',
                        'input_message': '''Integer > 0''',
                        'error_title': 'Error',
                        'error_message': 'Integer > 0'
                    }
                    }


sample_owner = make_string_dict('sample_owner')


# ==============================================================================
# For metadata fields
# ==============================================================================

title = make_string_dict('title')
title['valid']['input_message'] = 'A short descriptive title of the dataset'

abstract = make_string_dict('abstract')
abstract['valid'][
    'input_message'] = '''An abstract providing context for the dataset.
It should briefly explain the sampling and analysis procedures used to obtain the data.
Here it is possible to refer to a published protocol'''

pi_name = make_string_dict('pi_name')
pi_name['disp_name'] = 'Principal investigator (PI)'

pi_email = make_string_dict('pi_email')
pi_email['disp_name'] = 'PI email'

pi_institution = make_string_dict('pi_institution')
pi_institution['disp_name'] = 'PI institution'

pi_address = make_string_dict('pi_address')
pi_address['disp_name'] = 'PI address'

project_long = make_string_dict('project_long')
project_long['disp_name'] = 'Project long name'

project_short = make_string_dict('project_short')
project_short['disp_name'] = 'Project short name'


projectID = {'name': 'projectID',
             'disp_name': 'Project ID',
             'width': 40,
             'valid': {
                 'validate': 'any',
                 'input_title': 'Project ID',
                 'input_message': '''The project ID.
For the Nansen Legacy this is:
The Nansen Legacy (RCN # 276730)'''
             }
             }


# ==============================================================================
# Species names
# ==============================================================================

taxon = make_string_dict('Taxon')
taxon['dwcid'] = 'http://rs.tdwg.org/dwc/terms/Taxon'

phylum = make_string_dict('phylum')
phylum['dwcid'] = 'http://rs.tdwg.org/dwc/terms/phylum'

# can't call it class as that is a python word
sex = {'name': 'sex',
       'disp_name': 'Sex',
       'dwcid': 'http://rs.tdwg.org/dwc/terms/sex',
                'valid': {
                    'validate': 'any',
                    # 'source': ['Male', 'Female', 'Undetermined'],
                    'input_title': 'Sex',
                    'input_message': '''Male (M), female (F), maybe male (M?), maybe female (F?) or unknown (?)''',
                    # 'error_title': 'Error',
                    # 'error_message': 'Not a valid sex '
                }
       }
classify = make_string_dict('class')
classify['dwcid'] = 'http://rs.tdwg.org/dwc/terms/class'

order = make_string_dict('order')
order['dwcid'] = 'http://rs.tdwg.org/dwc/terms/order'

family = make_string_dict('family')
family['dwcid'] = 'http://rs.tdwg.org/dwc/terms/family'

scientificName = {'name': 'scientificName',
                  'disp_name': 'Scientific Name',
                  'width': 20,
                  'dwcid': 'http://rs.tdwg.org/dwc/terms/scientificName',
                  'valid': {
                      'validate': 'any',
                      'input_title': 'Scientific Name',
                      'input_message': '''The full scientific name, with authorship and date information if known.
When forming part of an Identification, this should be the name in lowest level taxonomic rank that can be determined'''
                  },
                  'cell_format': {
                      'left': True
                  }
                  }


dataFilename = {'name': 'dataFilename',
                'disp_name': 'Data filename',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Data filename',
                    'input_message': 'The name of the datafile'
                }
                }

serialNumber = {'name': 'serialNumber',
                'disp_name': 'Serial Number',
                'measurementType': 'Serial number of instrument',
                'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P01/current/SERNUMZZ/',
                'measurementUnit': 'NA',
                'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
                'valid': {
                    'validate': 'any',
                    'input_title': 'Instrument Serial Number',
                    'input_message': 'The serial number of the instrument used'
                }
                }

samplingProtocol = {'name': 'samplingProtocol',
                    'disp_name': 'Sampling protocol',
                    'valid': {
                        'validate': 'any',
                        'input_title': 'Sampling protocol',
                        'input_message': '''This should be a reference to the sampling protocol used.
For example: Nansen Legacy sampling protocols version XX section YY.'''
                    }
                    }

# This should be the same as is https://github.com/SIOS-Svalbard/AeN_doc/blob/master/list_sample_types.csv
gearType = {'name': 'gearType',
                    'disp_name': 'Gear Type',
                    'inherit': True,
                    'long_list': True,
                    'valid': {
                        'validate': 'list',
                        'source': __gear_types,
                        'input_title': 'Gear Type',
                        'input_message': 'Choose the gear used to retrieve the sample.\n' +
                                         'Listed at: https://github.com/SIOS-Svalbard/AeN_doc/blob/master/list_gear_types.csv',
                        'error_title': 'Error',
                        'error_message': 'Not a valid gear type'
                    }
            }

# This should be the same as is https://github.com/SIOS-Svalbard/AeN_doc/blob/master/list_sample_types.csv
sampleType = {'name': 'sampleType',
              'disp_name': 'Sample Type',
              'long_list': True,
              'valid': {
                  'validate': 'list',
                  'source': __sample_types,
                  'input_title': 'Sample type',
                  'input_message': 'Choose the sample type.\n' +
                                   'Listed at: https://github.com/SIOS-Svalbard/AeN_doc/blob/master/list_sample_types.csv',
                  'error_title': 'Error',
                  'error_message': 'Not a valid sample type'
              }
              }

tissueType = {'name': 'tissueType',
              'disp_name': 'Tissue Type',
              'measurementType': 'tissue',
              'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/S12/current/S1225/',
              'measurementUnit': 'NA',
              'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Tissue Type',
                  'input_message': '''The type of tissue in the sample.
If multiple tissue types, organs etc. separate with ';'.
Examples: 'heart', 'liver; brain', 'liver section' '''
              }
              }

intendedMethod = {'name': 'intendedMethod',
                  'disp_name': 'Intended Method',
                  'valid': {
                      'validate': 'any',
                      'input_title': 'Intended Method',
                      'input_message': '''The intended measurement method for the sample.
If multiple methods, separate with ';'.
Examples: 'FCM', 'XCM', 'SEM' '''
                  }
                  }

seaIceCoreType = {'name': 'seaIceCoreType',
                  'disp_name': 'Sea Ice Core Type',
                  'valid': {
                      'validate': 'any',
                      'input_title': 'Sea Ice Core Type',
                      'input_message': 'The analysis the sea ice core is intended for'
                  }
                  }

seaIceCoreLengthInMeters = {'name': 'seaIceCoreLengthInMeters',
                            'disp_name': 'Sea Ice Core Length (cm)',
                            'units': 'cm',
                            'measurementType': 'Sea ice core length',
                            'measurementTypeID': '',
                            'measurementUnit': 'Centimetres',
                            'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                            'valid': {
                                'validate': 'decimal',
                                'criteria': '>',
                                'value': 0,
                                'input_title': 'Sea Ice Core length (cm)',
                                'input_message': '''Sea ice core length in decimal centimeters.
 Float number larger than 0 ''',
                                'error_title': 'Error',
                                'error_message': 'Float > 0'
                            }
                            }

seaIceCoreMaximumDepthInCentiMeters = {'name': 'seaIceCoreMaximumDepthInCentiMeters',
                                         'disp_name': 'Sea Ice Core Maximum Depth (cm)',
                                         'units': 'cm',
                                         'measurementType': 'Sea ice core maximum depth',
                                         'measurementTypeID': '',
                                         'measurementUnit': 'Centimetres',
                                         'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                                         'valid': {
                                             'validate': 'decimal',
                                             'criteria': 'between',
                                             'minimum': 0,
                                             'maximum': 3000,
                                             'input_title': 'Sea Ice Core Maximum Depth (cm)',
                                             'input_message': '''The sea ice core maximum depth in centimeters.
This is measured from the top of the core, with 0 cm being the surface.
Maximum is 3 000 cm.''',
                                             'error_title': 'Error',
                                             'error_message': 'Float[0, 3 000]'
                                         }
                                         }


seaIceCoreMinimumDepthInCentiMeters = {'name': 'seaIceCoreMinimumDepthInCentiMeters',
                                         'disp_name': 'Sea Ice Core Minimum Depth (cm)',
                                         'units': 'cm',
                                         'measurementType': 'Sea ice core minimum depth',
                                         'measurementTypeID': '',
                                         'measurementUnit': 'Centimetres',
                                         'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                                         'valid': {
                                             'validate': 'decimal',
                                             'criteria': 'between',
                                             'minimum': 0,
                                             'maximum': 3000,
                                             'input_title': 'Sea Ice Core Minimum Depth (cm)',
                                             'input_message': '''The sea ice core minimum depth in centimeters.
This is measured from the top of the core, with 0 cm being the surface.''',
                                             'error_title': 'Error',
                                             'error_message': 'Float[0, 3 000]'
                                         }
                                         }

seaIceThicknessInMeters = {'name': 'seaIceThicknessInMeters',
                           'disp_name': 'Sea Ice Thickness (cm)',
                           'units': 'cm',
                           'measurementType': 'sea_ice_thickness',
                           'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/CFSN0369/',
                           'measurementUnit': 'Centimetres',
                           'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                           'valid': {
                               'validate': 'decimal',
                               'criteria': '>',
                               'value': 0,
                               'input_title': 'Sea Ice Thickness (cm)',
                               'input_message': '''Sea ice thickness in decimal centimeters.
 Float number larger than 0 ''',
                               'error_title': 'Error',
                               'error_message': 'Float > 0'
                           }
                           }
seaIceFreeboardInMeters = {'name': 'seaIceFreeboardInMeters',
                           'disp_name': 'Sea Ice Freeboard (cm)',
                           'units': 'cm',
                           'measurementType': 'sea_ice_freeboard',
                           'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/CFSN0365/',
                           'measurementUnit': 'Centimetres',
                           'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                           'valid': {
                               'validate': 'decimal',
                               'criteria': '>',
                               'value': 0,
                               'input_title': 'Sea Ice Freeboard (cm)',
                               'input_message': '''Sea ice freeboard in decimal centimeters.
 Float number larger than 0 ''',
                               'error_title': 'Error',
                               'error:message': 'Float > 0'
                           }
                           }
seaIceCoreTemperatureInCelsius = {'name': 'seaIceCoreTemperatureInCelsius',
                                       'disp_name': 'Sea Ice Core Temperature (C)',
                                       'units': 'Celsius',
                                       'measurementType': 'Sea ice core temperature',
                                       'measurementTypeID': '',
                                       'measurementUnit': 'Degrees Celsius',
                                       'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPAA/',
                                       'valid': {
                                           'validate': 'decimal',
                                           'criteria': '>',
                                           'value': -40,
                                           'input_title': 'Sea Ice Core Temperature (C)',
                                           'input_message': '''Sea ice core temperature in Celsius. Temperature measurements should be made in the field and the positions at which the measurements were made must be clearly specified.
 Float number larger than -40 ''',
                                           'error_title': 'Error',
                                           'error:message': 'Float > -40'
                                       }
                                       }
seaIceMeltpondTemperatureInCelsius = {'name': 'seaIceMeltpondTemperatureInCelsius',
                                       'disp_name': 'Sea Ice Meltpond Temperature (C)',
                                       'units': 'Celsius',
                                       'measurementType': 'Sea ice meltpond temperature',
                                       'measurementTypeID': '',
                                       'measurementUnit': 'Degrees Celsius',
                                       'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPAA/',
                                       'valid': {
                                           'validate': 'decimal',
                                           'criteria': '>',
                                           'value': -10,
                                           'input_title': 'Sea Ice Meltpond Temperature (C)',
                                           'input_message': '''Sea ice meltpond temperature in Celsius.
 Float number larger than -10 ''',
                                           'error_title': 'Error',
                                           'error:message': 'Float > -10'
                                       }
                                       }
seaIceMeltpondSalinity = {'name': 'seaIceMeltpondSalinity',
                          'disp_name': 'Sea Ice Meltpond Salinity (1e-3)',
                          'units': '1e-3',
                          'measurementType': 'Sea ice meltpond salinity',
                          'measurementTypeID': '',
                          'measurementUnit': 'Parts per thousand',
                          'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPPT/',
                          'valid': {
                              'validate': 'decimal',
                              'criteria': '>=',
                              'value': 0,
                              'input_title': 'Sea Ice Meltpond Saliniy Core length (cm)',
                              'input_title': 'Sea Ice Meltpond Salinity',
                              'input_message': '''Sea ice meltpond salinity in parts per thousand
Often using the Practical Salinity Scale of 1978
Float number larger than or equal to 0
Example: 0.029''',
                              'error_title': 'Error',
                              'error_message': 'Float >= 0'
                          }
                          }
# CF names

seaWaterTemperatueInCelsius = {'name': 'seaWaterTemperatueInCelsius',
                               'disp_name': 'Sea Water Temp (C)',
                               'inherit': True,
                               'units': 'Celsius',
                               'cf_name': 'sea_water_temperature',
                               'measurementType': 'sea_water_temperature',
                               'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/CFSN0335/',
                               'measurementUnit': 'Degrees Celsius',
                               'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPAA/',
                               'valid': {
                                   'validate': 'decimal',
                                   'criteria': '>',
                                   'value': -10,
                                   'input_title': 'Sea Water Temp (C)',
                                   'input_message': '''Sea water temperature in Celsius
Float number larger than -10 degrees C''',
                                   'error_title': 'Error',
                                   'error_message': 'Float > -10 C'
                               }
                               }

seaWaterPracticalSalinity = {'name': 'seaWaterPracticalSalinity',
                             'disp_name': 'Sea Water Practical Salinity (1)',
                             'inherit': True,
                             'units': '1',
                             'cf_name': 'sea_water_practical_salinity',
                             'measurementType': 'sea_water_practical_salinity',
                             'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/IADIHDIJ/',
                             'measurementUnit': 'NA',
                             'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
                             'valid': {
                                 'validate': 'decimal',
                                 'criteria': '>=',
                                 'value': 0,
                                 'input_title': 'Sea Water Practical Salinity',
                                 'input_message': '''Practical Salinity, S_P, is a determination of 
the salinity of sea water, based on its electrical conductance. 
The measured conductance, corrected for temperature and pressure,
is compared to the conductance of a standard potassium chloride 
solution, producing a value on the Practical Salinity Scale of 1978 (PSS-78).
Float number larger than or equal to 0
Example: 29.003''',
                                 'error_title': 'Error',
                                 'error_message': 'Float >= 0'
                             }
                             }

seaWaterAbsoluteSalinity = {'name': 'seaWaterAbsoluteSalinity',
                            'disp_name': 'Sea Water Absolute Salinity (g/kg)',
                            'inherit': True,
                            'units': 'g kg-1',
                            'cf_name': 'sea_water_absolute_salinity',
                            'measurementType': 'sea_water_absolute_salinity',
                            'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/JIBGDIEJ/',
                            'measurementUnit': 'Grams per kilogram',
                            'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UGKG/',
                            'valid': {
                                'validate': 'decimal',
                                'criteria': '>=',
                                'value': 0,
                                'input_title': 'Sea Water Absolute Salinity',
                                'input_message': '''Absolute Salinity, S_A, is defined as part of 
the Thermodynamic Equation of Seawater 2010 (TEOS-10) which was
adopted in 2010 by the Intergovernmental Oceanographic 
Commission (IOC). It is the mass fraction of dissolved material
in sea water.
Float number larger than or equal to 0
Example: 3.5''',
                                'error_title': 'Error',
                                'error_message': 'Float >= 0'
                            }
                            }

seaWaterElectricalConductivity = {'name': 'seaWaterElectricalConductivity',
                                  'disp_name': 'Sea Water Conductivity (S/m)',
                                  'inherit': True,
                                  'units': 's m-1',
                                  'cf_name': 'sea_water_electrical_conductivity',
                                  'measurementType': 'sea_water_electrical_conductivity',
                                  'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/CFSN0394/',
                                  'measurementUnit': 'Siemens per metre',
                                  'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UECA/',
                                  'valid': {
                                      'validate': 'decimal',
                                      'criteria': '>=',
                                      'value': 0,
                                      'input_title': 'Sea Water Conductivity',
                                      'input_message': '''Sea water electrical conductivity in siemens per meter
Float number larger than or equal to 0
Example: 3.0''',
                                      'error_title': 'Error',
                                      'error_message': 'Float >= 0'
                                  }
                                  }

seaWaterPressure = {'name': 'seaWaterPressure',
                    'disp_name': 'Sea Water Pressure (dbar)',
                    'inherit': True,
                    'units': 'dbar',
                    'cf_name': 'sea_water_pressure',
                    'measurementType': 'sea_water_pressure',
                    'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/CFSN0330/',
                    'measurementUnit': 'Decibars',
                    'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPDB/',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>',
                        'value': 0,
                        'input_title': 'Sea Water Pressure (dbar)',
                        'input_message': '''Sea water pressure in decibar
Float number larger than 0''',
                        'error_title': 'Error',
                        'error_message': 'Float > 0'
                    }
                    }


seaWaterChlorophyllA = {'name': 'seaWaterChlorophyllA',
                        'disp_name': 'Sea Chl A (mg/m^3)',
                        'units': 'mg m-3',
                        'measurementType': 'mass_concentration_of_chlorophyll_a_in_sea_water',
                        'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/CF14N7/',
                        'measurementUnit': 'Milligrams per square metre',
                        'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMMS/',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>=',
                            'value': 0,
                            'input_title': 'Sea Water Chlorophyll A (mg/m^3)',
                            'input_message': '''
Sea Water Chlorophyll in milligrams per cubic meter
Positive float number (>= 0)''',
                            'error_title': 'Error',
                            'error_message': 'Float >= 0'
                        }
                        }

seaWaterPhaeopigment = {'name': 'seaWaterPhaeopigment',
                        'disp_name': 'Sea Phaeo (mg/m^3)',
                        'units': 'mg m-3',
                        'measurementType': 'mass_concentration_of_phaeopigment_in_sea_water',
                        'measurementTypeID': '',
                        'measurementUnit': 'Milligrams per square metre',
                        'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMMS/',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>',
                            'value': 0,
                            'input_title': 'Sea Water Phaeopigment (mg/m^3)',
                            'input_message': '''
Sea Water Phaeopigment in milligrams per cubic meter
Positive float number''',
                            'error_title': 'Error',
                            'error_message': 'Float > 0'
                        }
                        }

seaIceChlorophyllA = {'name': 'seaIceChlorophyllA',
                      'disp_name': 'Ice Chl A (mg/m^3)',
                      'units': 'mg m-3',
                      'measurementType': 'mass_concentration_of_chlorophyll_a_in_sea_ice',
                      'measurementTypeID': '',
                      'measurementUnit': 'Milligrams per square metre',
                      'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMMS/',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>=',
                          'value': 0,
                          'input_title': 'Sea Ice Chlorophyll a (mg/m^3)',
                          'input_message': '''
Sea Ice Chlorophyll in milligrams per cubic meter
Positive float number (>= 0)''',
                          'error_title': 'Error',
                          'error_message': 'Float >= 0'
                      }
                      }

seaIcePhaeopigment = {'name': 'seaIcePhaeopigment',
                      'disp_name': 'Ice Phaeo (mg/m^3)',
                      'units': 'mg m-3',
                      'measurementType': 'mass_concentration_of_phaeopigment_in_sea_ice',
                      'measurementTypeID': '',
                      'measurementUnit': 'Milligrams per square metre',
                      'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMMS/',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Sea Ice Phaeopigment (mg/m^3)',
                          'input_message': '''
Sea Ice Phaeopigment in milligrams per cubic meter
Positive float number''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      }

sedimentChlorophyllA = {'name': 'sedimentChlorophyllA',
                        'disp_name': 'Sediment Chl A (mg/m^3)',
                        'units': 'mg m-3',
                        'measurementType': 'Chlorophyll-a in sediment',
                        'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P09/current/CHAS/',
                        'measurementUnit': 'Milligrams per square metre',
                        'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMMS/',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>=',
                            'value': 0,
                            'input_title': 'Sediment Chlorophyll a (mg/m^3)',
                            'input_message': '''
Sediment Chlorophyll in milligrams per cubic meter
Positive float number (>= 0)''',
                            'error_title': 'Error',
                            'error_message': 'Float >= 0'
                        }
                        }

sedimentPhaeopigment = {'name': 'sedimentPhaeopigment',
                        'disp_name': 'Sediment Phaeo (mg/m^3)',
                        'units': 'mg m-3',
                        'measurementType': 'mass_concentration_of_phaeopigment_in_sediment',
                        'measurementTypeID': '',
                        'measurementUnit': 'Milligrams per square metre',
                        'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMMS/',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>',
                            'value': 0,
                            'input_title': 'Sediment Phaeopigment (mg/m^3)',
                            'input_message': '''
Sediment Phaeopigment in milligrams per cubic meter
Positive float number''',
                            'error_title': 'Error',
                            'error_message': 'Float > 0'
                        }
                        }

sedimentPH = {'name': 'sedimentPH',
              'disp_name': 'Sediment pH  (total scale)',
              'units': '1',
              'measurementType': 'pH in the sediment',
              'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P35/current/EPC00136/',
              'measurementUnit': 'NA',
              'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
              'valid': {
                  'validate': 'decimal',
                  'criteria': 'between',
                  'minimum': -2,
                  'maximum': 16,
                  'input_title': 'Sediment  pH  (total scale)',
                  'input_message': '''
Is the measure of acidity of seawater, defined as the negative logarithm of
the concentration of dissolved hydrogen ions plus bisulfate ions in a sea water
medium; it can be measured or calculated; when measured the scale is defined
according to a series of buffers prepared in artificial seawater containing
bisulfate.
Float in range [-2, 16]''',
                  'error_title': 'Error',
                  'error_message': 'Not in range [-2, 16]'
              }
              }

sedimentTOC = {'name': 'sedimentTOC',
               'disp_name': 'Sediment TOC (mg/L)',
               'units': 'mg L-1',
               'measurementType': 'SEDIMENT TOTAL ORGANIC CARBON',
               'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P09/current/TOCS/',
               'measurementUnit': 'Milligrams per litre',
               'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMGL/',
               'valid': {
                   'validate': 'decimal',
                   'criteria': '>=',
                   'value': 0,
                   'input_title': 'Sediment TOC (mg/L)',
                   'input_message': '''
Sediment Total Organic Carbon in milligrams per litre
Positive float number''',
                   'error_title': 'Error',
                   'error_message': 'Float >= 0'
               }
               }

sedimentTN = {'name': 'sedimentTN',
              'disp_name': 'Sediment TN (mg/L)',
              'units': 'mg L-1',
              'measurementType': 'SEDIMENT TOTAL NITROGEN',
              'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P09/current/TNNS/',
              'measurementUnit': 'Milligrams per litre',
              'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMGL/',
              'valid': {
                  'validate': 'decimal',
                  'criteria': '>=',
                  'value': 0,
                  'input_title': 'Sediment TN (mg/L)',
                  'input_message': '''
Sediment Total Nitrogen in milligrams per litre
Positive float number''',
                  'error_title': 'Error',
                  'error_message': 'Float >= 0'
              }
              }
benthicRespiration = {'name': 'benthicRespiration',
                      'disp_name': 'Benthic Respiration (mmol/m^2)',
                      'units': 'mmol m-2',
                      'measurementType': 'Benthic respiration of oxygen',
                      'measurementTypeID': '',
                      'measurementUnit': 'Millimoles per square metre',
                      'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/MMSM/',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>=',
                          'value': 0,
                          'input_title': 'Benthic Respiration (mmol/m^2)',
                          'input_message': '''
Benthic respiration of Oxygen in millimole per square meter
Positive float number''',
                          'error_title': 'Error',
                          'error_message': 'Float >= 0'
                      }
                      }

seaWaterTotalDIC = {'name': 'seaWaterTotalDIC',
                    'disp_name': 'Sea DIC (umol/kg)',
                    'units': 'umol kg-1',
                    'measurementType': 'mole_concentration_of_dissolved_inorganic_carbon_in_sea_water',
                    'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/CF14N27/',
                    'measurementUnit': 'Micromoles per kilogram',
                    'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/KGUM/',
                    'cf_name': 'mole_concentration_of_dissolved_inorganic_carbon_in_sea_water',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>=',
                        'value': 0,
                        'input_title': 'Sea Water DIC (umol/kg)',
                        'input_message': '''
Sea Water Total dissolved inorganic carbon in umol per kg
Positive float number''',
                        'error_title': 'Error',
                        'error_message': 'Float >= 0'
                    }
                    }

seaIceTotalDIC = {'name': 'seaIceTotalDIC',
                  'disp_name': 'Ice DIC (umol/kg)',
                  'units': 'umol kg-1',
                  'measurementType': 'mole_concentration_of_dissolved_inorganic_carbon_in_sea_ice',
                  'measurementTypeID': '',
                  'measurementUnit': 'Micromoles per kilogram',
                  'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/KGUM/',
                  'valid': {
                      'validate': 'decimal',
                      'criteria': '>=',
                      'value': 0,
                      'input_title': 'Sea Ice DIC (umol/kg)',
                      'input_message': '''
Sea Ice Total dissolved inorganic carbon in umol per kg
Positive float number''',
                      'error_title': 'Error',
                      'error_message': 'Float >= 0'
                  }
                  }

seaWaterDeltaO18 = {'name': 'seaWaterDeltaO18',
                    'disp_name': 'Sea delta-O-18 (1e-3)',
                    'units': '1e-3',
                    'measurementType': 'ISOTOPIC RATIO O18/O16',
                    'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P09/current/OXIR/',
                    'measurementUnit': 'Parts per thousand',
                    'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPPT/',
                    'valid': {
                        'validate': 'decimal',
                        'criteria': '>=',
                        'value': 0,
                        'input_title': 'Sea Water delta-O-18 (1e-3)',
                        'input_message': '''
Sea Water delta-O-18 in parts per thousand
Positive float number''',
                        'error_title': 'Error',
                        'error_message': 'Float >= 0'
                    }
                    }

seaIceDeltaO18 = {'name': 'seaIceDeltaO18',
                  'disp_name': 'Ice delta-O-18 (1e-3)',
                  'units': '1e-3',
                  'measurementType': 'ISOTOPIC RATIO O18/O16',
                  'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P09/current/OXIR/',
                  'measurementUnit': 'Parts per thousand',
                  'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UPPT/',
                  'valid': {
                      'validate': 'decimal',
                      'criteria': '>=',
                      'value': 0,
                      'input_title': 'Sea Ice delta-O-18 (1e-3)',
                      'input_message': '''
Sea Ice delta-O-18 in parts per thousand
Positive float number''',
                      'error_title': 'Error',
                      'error_message': 'Float >= 0'
                  }
                  }

seaWaterPH = {'name': 'seaWaterPH',
              'disp_name': 'Sea Water pH  (total scale)',
              'units': '1',
              'cf_name': 'sea_water_ph_reported_on_total_scale',
              'measurementType': 'sea_water_ph_reported_on_total_scale',
              'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P07/current/CF14N56/',
              'measurementUnit': 'NA',
              'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
              'valid': {
                  'validate': 'decimal',
                  'criteria': 'between',
                  'minimum': -2,
                  'maximum': 16,
                  'input_title': 'Sea Water pH  (total scale)',
                  'input_message': '''
Is the measure of acidity of seawater, defined as the negative logarithm of
the concentration of dissolved hydrogen ions plus bisulfate ions in a sea water
medium; it can be measured or calculated; when measured the scale is defined
according to a series of buffers prepared in artificial seawater containing
bisulfate.
Float in range [-2, 16]''',
                  'error_title': 'Error',
                  'error_message': 'Not in range [-2, 16]'
              }
              }

seaWaterAlkalinity = {'name': 'seaWaterAlkalinity',
                      'disp_name': 'Total Alkalinity (umol/kg)',
                      'units': 'umol kg-1',
                      'measurementType': 'Total alkalinity per unit mass of the water body',
                      'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P01/current/MDMAP014/',
                      'measurementUnit': 'Micromoles per kilogram',
                      'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/KGUM/',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>=',
                          'value': 0,
                          'input_title': 'Sea Water Total Alkalinity (umol/kg)',
                          'input_message': '''
Sea Water Total Alkalinity in micromols per kilogram
Positive float number''',
                          'error_title': 'Error',
                          'error_message': 'Float >= 0'
                      }
                      }

seaWaterTOC = {'name': 'seaWaterTOC',
               'disp_name': 'TOC (mg/L)',
               'units': 'mg L-1',
               'measurementType': 'TOTAL ORGANIC CARBON',
               'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P09/current/TOCW/',
               'measurementUnit': 'Milligrams per litre',
               'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UMGL/',
               'valid': {
                   'validate': 'decimal',
                   'criteria': '>=',
                   'value': 0,
                   'input_title': 'TOC (mg/L)',
                   'input_message': '''
Sea Water Total Organic Carbon in milligrams per litre
Positive float number''',
                   'error_title': 'Error',
                   'error_message': 'Float >= 0'
               }
               }

seaWaterPON = {'name': 'seaWaterPON',
               'disp_name': 'PON (ug/L)',
               'units': 'ug L-1',
               'measurementType': 'Water body particulate nitrogen',
               'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P35/current/EPC00212/',
               'measurementUnit': 'Micrograms per litre',
               'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UGPL/',
               'valid': {
                   'validate': 'decimal',
                   'criteria': '>=',
                   'value': 0,
                   'input_title': 'PON (ug/L)',
                   'input_message': '''
Sea Water Quantification of particulate organic nitrogen in micrograms per litre
Positive float number''',
                   'error_title': 'Error',
                   'error_message': 'Float >= 0'
               }
               }


seaWaterPOC = {'name': 'seaWaterPOC',
               'disp_name': 'POC (ug/L)',
               'units': 'ug L-1',
               'measurementType': 'Water body particulate organic carbon {POC}',
               'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P35/current/EPC00157/',
               'measurementUnit': 'Micrograms per litre',
               'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UGPL/',
               'valid': {
                   'validate': 'decimal',
                   'criteria': '>=',
                   'value': 0,
                   'input_title': 'POC (ug/L)',
                   'input_message': '''
Sea Water Quantification of particulate organic carbon  in micrograms per litre
Positive float number''',
                   'error_title': 'Error',
                   'error_message': 'Float >= 0'
               }
               }


weightInGrams = {'name': 'weightInGrams',
                 'disp_name': 'Weight (g)',
                 'units': 'g',
                 'measurementType': 'mass',
                 'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/P21/current/MS6179/',
                 'measurementUnit': 'Grams',
                 'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UGRM/',
                 'valid': {
                     'validate': 'decimal',
                     'criteria': '>',
                     'value': 0,
                     'input_title': 'Weight in grams (g)',
                     'input_message': '''Weight in grams''',
                     'error_title': 'Error',
                     'error_message': 'Float > 0'
                 }
                 }
gonadWeightInGrams = {'name': 'gonadWeightInGrams',
                      'disp_name': 'Gonad Weight (g)',
                      'units': 'g',
                      'measurementType': 'Gonad weight',
                      'measurementTypeID': '',
                      'measurementUnit': 'Grams',
                      'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UGRM/',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Gonad Weight in grams (g)',
                          'input_message': '''Wet weight of the gonad in in grams''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      }

liverWeightInGrams = {'name': 'liverWeightInGrams',
                      'disp_name': 'Liver Weight (g)',
                      'units': 'g',
                      'measurementType': 'Liver weight',
                      'measurementTypeID': '',
                      'measurementUnit': 'Grams',
                      'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UGRM/',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Liver Weight in grams (g)',
                          'input_message': '''Wet weight of the liver in in grams''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      }
somaticWeightInGrams = {'name': 'somaticWeightInGrams',
                        'disp_name': 'Somatic Weight (g)',
                        'units': 'g',
                        'measurementType': 'Somatic weight',
                        'measurementTypeID': '',
                        'measurementUnit': 'Grams',
                        'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/UGRM/',
                        'valid': {
                            'validate': 'decimal',
                            'criteria': '>',
                            'value': 0,
                            'input_title': 'Somatic Weight in grams (g)',
                            'input_message': '''Wet weight of the fish when all inner organs are removed from the fish gonad in in grams''',
                            'error_title': 'Error',
                            'error_message': 'Float > 0'
                        }
                        }

forkLengthInMeters = {'name': 'forkLengthInMeters',
                      'disp_name': 'Fork length (cm)',
                      'units': 'cm',
                      'measurementType': 'Fork length',
                      'measurementTypeID': '',
                      'measurementUnit': 'Centimetres',
                      'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Fork lenght (cm)',
                          'input_message': '''The length of a fish measured from the most anterior part of the head to the deepest point of the notch in the tail fin in cm.
Positive decimal number''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      }
totalFishLengthInMeters = {'name': 'totalFishLengthInMeters',
                      'disp_name': 'Total fish length (cm)',
                      'units': 'cm',
                      'measurementType': 'Total fish length',
                      'measurementTypeID': '',
                      'measurementUnit': 'Centimetres',
                      'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/ULCM/',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Total lenght (cm)',
                          'input_message': '''The length of a fish measured from the tip of the snout to the tip of the longer lobe of the caudal fin, usually measured with the lobes compressed along the midline. It is a straight-line measure, not measured over the curve of the body.
Positive decimal number in cm.''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      }
lengthInMeters = {'name': 'lengthInMeters',
                      'disp_name': 'Length (m)',
                      'units': 'm',
                      #                  'dwcid': 'http://rs.tdwg.org/dwc/terms/dynamicProperties',
                      'valid': {
                          'validate': 'decimal',
                          'criteria': '>',
                          'value': 0,
                          'input_title': 'Length (m)',
                          'input_message': '''A measurement of length in meters. This is a universal parameter and should only be used if there is not any other length parameter that fits.
Positive decimal number in m.''',
                          'error_title': 'Error',
                          'error_message': 'Float > 0'
                      }
                      }
maturationStage = {'name': 'maturationStage',
                   'disp_name': 'Maturation Stage',
                   'units': '1',
                   'measurementType': 'Maturation stage',
                   'measurementTypeID': 'http://vocab.nerc.ac.uk/collection/S11/current/',
                   'measurementUnit': 'NA',
                   'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
                   'valid': {
                       'validate': 'decimal',
                       'criteria': 'between',
                       'minimum': 0,
                       'maximum': 7,
                       'input_title': 'Maturation Stage',
                       'input_message': '''On the basis of shape, size, color of the gonads and other morphological features, at least six maturity stages can be recognized
Decimal value in range [0, 7]''',
                       'error_title': 'Error',
                       'error_message': 'Decimal range [0, 7]'
                   }
                   }

ectoparasites = {'name': 'ectoparasites',
                 'disp_name': 'Ectoparasites',
                 'units': '1',
                 'measurementType': 'Ectoparasites',
                 'measurementTypeID': '',
                 'measurementUnit': 'NA',
                 'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
                 'valid': {
                     'validate': 'integer',
                       'criteria': 'between',
                       'minimum': 0,
                       'maximum': 1,
                     'input_title': 'Ectoparasites',
                     'input_message': '''Presence (1) or absence (0) of visible parasites on the fins and gills of the fish
Integer [0, 1]''',
                     'error_title': 'Error',
                     'error_message': 'Int range [0, 1]'
                 }
                 }

endoparasites = {'name': 'endoparasites',
                 'disp_name': 'Endoparasites',
                 'units': '1',
                 'measurementType': 'Endoparasites',
                 'measurementTypeID': '',
                 'measurementUnit': 'NA',
                 'measurementUnitID': 'http://vocab.nerc.ac.uk/collection/P06/current/XXXX/',
                 'valid': {
                     'validate': 'integer',
                       'criteria': 'between',
                       'minimum': 0,
                       'maximum': 1,
                     'input_title': 'Endoparasites',
                     'input_message': '''Presence (1) or absence (0) of visible parasites of endoparasites visible in the body cavity of the fish
Integer [0, 1]''',
                     'error_title': 'Error',
                     'error_message': 'Int range [0, 1]'
                 }
                 }


# For BIG
instrument = {'name': 'instrument',
              'disp_name': 'Instrument Name',
              'valid': {
                  'validate': 'any',
                  'input_title': 'Instrument Name',
                  'input_message': '''This is the instrument name with brand
Example: Camera (Nikon D7000), Temperature logger (Onset HOBO)'''
              }
              }

objective = {'name': 'objective',
             'disp_name': 'Objective',
             'valid': {
                 'validate': 'any',
                 'input_title': 'Objective',
                 'input_message': '''Could be one word describing what the objective is.
Example: Melting, Reindeer,....'''
             }
             }

risID = {'name': 'risID',
         'disp_name': 'RISID',
         'valid': {
                 'validate': 'any',
                 'input_title': 'RIS ID(s)',
                 'input_message': '''The RIS ID(s).
The Research in Svalbard ID(s), comma separated if there is more than one'''
         }
         }

# List of all the available fields
fields = [getattr(sys.modules[__name__], item) for item in dir() if not item.startswith(
    "__") and isinstance(getattr(sys.modules[__name__], item), dict)]
