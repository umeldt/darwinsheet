#!/usr/bin/python3
# encoding: utf-8
'''
 -- Imports an xlsx sheet, converts it to a csv file, reads it, and checks the fields


@author:     Pål Ellingsen
@contact:    pale@unis.no
@deffield    updated: Updated
'''
import sys
import uuid
import io
import rdflib
import yaml
import pandas as pd
import numpy as np
import datetime as dt
import xml.etree.ElementTree
import xlsxwriter as xl
from xlrd import XLRDError
from argparse import ArgumentParser, RawDescriptionHelpFormatter, Namespace


import os.path
aen_config_dir = (os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

sys.path.append(aen_config_dir+'/scripts')
sys.path.append(aen_config_dir+'/config')
from make_xlsx import Field  # noqa: E402
import fields as fields  # noqa: E402

__all__ = []
__version__ = 0.1
__date__ = '2018-08-11'
__updated__ = '2019-03-06'

DEBUG = 1

# REQUIERED = ['eventID',
# 'cruiseNumber',
# 'stationName',
# 'eventTime',
# 'eventDate',
# 'decimalLatitude',
# 'decimalLongitude',
# 'bottomDepthInMeters',
# 'eventRemarks',
# 'samplingProtocol',
# 'parentEventID',
# 'sampleLocation',
# 'pi_name',
# 'pi_email',
# 'pi_institution',
# 'recordedBy',
# 'sampleType']


class Term:
    '''
    Class for reading holding rdf terms
    '''

    terms = []

    @staticmethod
    def get(id):
        for t in Term.terms:
            if t.uri == id or t.name == id:
                return t
        return Term(id)

    def __init__(self, uri):
        self.uri = uri
        self.name = uri.rsplit("/", 1)[-1]
        self.labels = {}
        self.examples = {}
        self.definitions = {}
        self.validations = {}
        Term.terms.append(self)

    def __lt__(self, other):
        #         print(self.uri, other.uri)
        return self.name.casefold() < other.name.casefold()

    def __eq__(self, other):
        return self.name.casefold() == other.name.casefold()

    def translate(self, d, lang):
        if lang in d:
            return d[lang]
        if '_' in d:
            return d['_']
        return ""

    def label(self, lang=None):
        return self.translate(self.labels, lang)

    def example(self, lang=None):
        return self.translate(self.examples, lang)

    def definition(self, lang=None):
        return self.translate(self.definitions, lang)

    def validation(self, lang=None):
        return self.translate(self.validations, lang)


def make_valid_dict():
    """
    Makes a dictionary of the possible fields with their validation.
    Does this by reading the fields list from the fields.py library, the 
    dwcterms.rdf (Darwin core) file  and dcterms.rdf (Dublin Core) 

    Returns
    ---------
    field_dict : dict
        Dictionary of the possible fields
        Contains a Checker object under each name


    """
    # First we go through the fields.py
    field_dict = {}
    for field in fields.fields:
        new = Checker(name=field['name'], disp_name=field['disp_name'])
        if 'valid' in field:
            new.set_validation(field['valid'])
        if 'inherit' in field:
            new.inherit = field['inherit']
        if 'units' in field:
            new.units = field['units']
#             print(new.validation)
        field_dict[field['name']] = new

    g = rdflib.Graph()
    g.load(os.path.join(aen_config_dir, "dwcterms.rdf"))
    def_valid = {'validate': 'any'}
    # Populate the terms with the terms from dwc
    for s, p, o in g:
        if str(p) == "http://www.w3.org/2000/01/rdf-schema#label":
            term = Term.get(s)
            term.labels['en'] = str(o)
            if term.name not in field_dict.keys():
                new = Checker(
                    name=term.name, disp_name=term.labels['en'])
                new.set_validation(def_valid)
                field_dict[term.name] = new

    g.load(os.path.join(aen_config_dir, "dcterms.rdf"))
    # Populate the terms with the terms from dublin core
    for s, p, o in g:
        if str(p) == "http://www.w3.org/2000/01/rdf-schema#label":
            term = Term.get(s)
            term.labels['en'] = str(o)
            if term.name not in field_dict.keys():
                new = Checker(
                    name=term.name, disp_name=term.labels['en'])
                new.set_validation(def_valid)
                field_dict[term.name] = new

    return field_dict


def xlsx_to_array(url, sheetname='Data', skiprows=1, **kwds):
    """
    Convert xlsx to numpy 2D array of objects

    Parameters
    ---------

    url: string or io
        Can either be a path or and io object

    sheetname: str
        The sheet name for the sheet in the xlsx file wanted
        Default: 'Data'

    skiprows: int
        The numper of rows to skip
        Default: 2

    **kwds : dict
        Keywords to be passed to pandas excel read

    Returns
    ---------

    data: numpy ndarray
        A numpy ndarray of objects for the sheet.
    """

    if isinstance(url, str):

        url = os.path.abspath(url)
    data = pd.read_excel(url, sheet_name=sheetname,
                         skiprows=skiprows, **kwds).values

    # Convert Timestamps to dates
    return data


def format_num(num):
    """
    Convert a string with a number to a number by removing common mistakes
    in Excel.
    Converts ',' to '.'
    Removes leading "'"
    If resulting string can be converted to an int, it is returned as an int,
    if not, it is returned as a float. If it can not be converted to a float,
    it throws a ValueError.


    Parameters
    ---------

    num: object
        The number to be converted.
        If it is an int or float, nothing is done with it.
        Needs to be convertible into a string.
    Returns
    ---------

    out: int or float
        The resulting int or float.
    """

    if isinstance(num, int) or isinstance(num, float):
        return num

    num_str = str(num).replace(',', '.').replace("'", '')

    try:
        out = int(num_str)
    except ValueError:
        out = float(num_str)
    return out


def is_nan(value):
    """
    Checks if value is 'nan' or NaT

    Parameters
    ---------

    value: object
        The object to be checked that it is not nan

    Returns
    ---------

    isnan: Boolean
        True: nan
        False: not nan
    """
    isnan = str(value).lower() == 'nan'
    isnat = str(value).lower() == 'nat'
    return isnan or isnat


class Evaluator(object):
    """ An object for holding a function for evaluating a type of data.
    The function should take two arguments, self and a value. By referencing and
    setting values on the object with self, it is possible to evaluate on
    multiple conditions."""

    def __init__(self, validation, func=None):
        """
        Initialise the Evaluator object.

        Parameters
        ---------

        validation: dict
            A dict containing the validation information.
            Can be used in evaluator function by referencing the property
            self.validation

        func: lambda function, optional
            This function should take two inputs, self and a value.
            If this is not set here, it needs to be set using the set_func
            method
            Should return a boolean, where True means the value has passed the
            test
            An example of a functions is:
            lambda self,x : self.valid['value'] < len(x)

        """

        self.validation = validation
        self.eval = func

    def set_func(self, func):
        """
        Method for setting the evaluator function.


        Parameters
        ---------

        func: lambda function, optional
            This function should take two inputs, self and a value.
            If this is not set here, it needs to be set using the set_func
            method
            Should return a boolean, where True means the value has passed the
            test
            An example of a functions is:
            lambda self, x : self.valid['value'] < len(x)
        """

        self.eval = func

    def evaluate(self, value):
        """
        Evaluate value with the evaluator

        Parameters
        ---------

        value: object
            The value to be evaluated
            Needs to be in a format that the function understands

        Returns
        ---------

        res: Boolean
            The result from the evaluator
            True, means that the value passed the evaluation
        """

        if self.eval == None:
            raise NameError(
                "No evaluator, set it during initialisation or with the 'set_func' method")

        try:
            res = self.eval(self, value)
        except TypeError:
            res = False
        if not(isinstance(res, bool)):
            raise ValueError(
                "The evaluator function is not returning a boolean")
        return res


class Checker(Field):
    """
    Object for holding the specification of a cell, and the validation of it
    Inherits from Field"""

    def __init__(self, inherit=False, units=None, *args, **kwargs):
        """
        Initialising the object

        Parameters
        ---------

        inherit: Boolean, optional
            Should the given field be inherited.
            Default: False

        units: string, optional
            The units of the field

        *args: arguments for Field

        **kwargs: keyword arguments for Field

        """
        Field.__init__(self, *args, **kwargs)
        if self.validation != {}:
            self.validator = get_validator(self.validation)
        else:
            self.validator = lambda x: True

        self.inherit = inherit
        self.units = units

    def set_validation(self, validation):
        """
        Method for setting the validation by reading the dictionary
        and converting it using the

        Parameters
        ---------

        validation: dict
            The specifications of the validation as a dict
            See the valid dict in Fields for details

        """

        Field.set_validation(self, validation)
        self.validator = self.get_validator(self.validation)

    def get_validator(self, validation=None):
        """
        Checks a parameter according to the defined validation

        Parameters
        ---------

        validation: dict, optional
            The valid dictionary defined in the fields.py file
            If not set, reads from the object

        Returns
        ---------

        validator: Evaluator
            A validator in the form of an Evaluator object

        """

        if validation == None:
            validation = self.validation

        validate = validation['validate']
        if validate == 'any':
            return Evaluator(validation, func=lambda self, x: isinstance(str(x), str))
        elif validate == 'list':
            source = validation['source']
            return Evaluator(source, func=lambda self, x: str(x) in self.validation)

        criteria = validation['criteria']

        def _formula_to_date(formula):
            """
            Internal function for converting validation date functions (Excel
            function) to a datetime date object

            Parameters
            ---------

            formula: str
                The Excel formula to be converted
                Supports simple addition and subtraction and the function TODAY

            Returns
            ---------

            date: datetime date object
                The resulting date from the formula
            """

            form = formula.replace('=', '')
            if 'TODAY()' in form:
                form = form.replace('TODAY()', 'dt.date.today()')
            if '+' in form:
                parts = form.split('+')
                parts[1] = 'dt.timedelta(days=' + parts[1] + ')'
                form = parts[0] + '+' + parts[1]
            elif '-' in form:
                parts = form.split('-')
                parts[1] = 'dt.timedelta(days=' + parts[1] + ')'
                form = parts[0] + '-' + parts[1]
            return eval(form)

        if validate == 'length':
            if criteria == 'between':
                return Evaluator(validation, func=lambda self, x: self.validation['minimum'] <= len(x) <= self.validation['maximum'])
            else:
                return Evaluator(validation, func=lambda self, x: eval("len(x) " + self.validation['criteria'] + str(self.validation['value'])))
        elif validate == 'decimal':
            if criteria == 'between':
                return Evaluator(validation, func=lambda self, x: (isinstance(x, int) or isinstance(x, float)) and self.validation['minimum'] <= float(x) <= self.validation['maximum'])
            else:
                return Evaluator(validation, func=lambda self, x: (isinstance(x, int) or isinstance(x, float)) and eval("float(x) " + self.validation['criteria'] + "self.validation['value']"))
        elif validate == 'integer':
            if criteria == 'between':
                return Evaluator(validation, func=lambda self, x: isinstance(x, int) and self.validation['minimum'] <= int(x) <= self.validation['maximum'])
            else:
                return Evaluator(validation, func=lambda self, x: isinstance(x, int) and eval("int(x) " + self.validation['criteria'] + "int(self.validation['value'])"))
        elif validate == 'time':
            if criteria == 'between':
                if isinstance(validation['minimum'], float) or isinstance(validation['minimum'], int):
                    minimum = (dt.datetime(1, 1, 1, 0, 0) +
                               dt.timedelta(days=validation['minimum'])).time()
                    maximum = (dt.datetime(1, 1, 1, 0, 0) +
                               dt.timedelta(days=validation['maximum'])).time()
                else:
                    minimum = validation['minimum']
                    maximum = validation['maximum']
                ev = Evaluator(validation)
                ev.minimum = minimum
                ev.maximum = maximum
                ev.set_func(lambda self, x: self.minimum <= x <= self.maximum)
                return ev
            else:
                if isinstance(validation['value'], float) or isinstance(validation['value'], int):
                    limit = (dt.datetime(1, 1, 1, 0, 0) +
                             dt.timedelta(days=validation['value'])).time()
                else:
                    limit = validation['value']

                ev = Evaluator(validation)
                ev.limit = limit
                ev.set_func(lambda self, x: eval(
                    "x" + self.validation['criteria'] + "self.limit"))
                return ev
        elif validate == 'date':
            # print("Date")
            if criteria == 'between':
                # print("Between")
                minimum = validation['minimum']
                maximum = validation['maximum']
                if not(isinstance(minimum, dt.date)):
                    # We now have a formula
                    minimum = _formula_to_date(minimum)
                if not(isinstance(maximum, dt.date)):
                    # We now have a formula
                    maximum = _formula_to_date(maximum)
                ev = Evaluator(validation)
                ev.minimum = minimum
                ev.maximum = maximum
                ev.set_func(lambda self, x: self.minimum <= x <= self.maximum)
                # ev.set_func(lambda self,x: print(self.minimum , x , self.maximum))
                return ev

            else:
                limit = validation['value']
                if not(isinstance(limit, dt.date)):
                    # We now have a formula
                    limit = _formula_to_date(limit)

                ev = Evaluator(validation)
                ev.limit = limit

                ev.set_func(lambda self, x: eval(
                    "x" + self.validation['criteria'] + "self.limit"))

                return ev
            # print(valid)
            raise NotImplementedError("No validator available for the object")


def check_value(value, checker):
    """
    Check the value with the checker.
    Does some additional checks in addition to the checks in checker

    Parameters
    ---------

    value: object
        The value to be checked

    checker: Checker
        The Checker to use

    Returns
    ---------

    bool : Boolean
        True, passed
        False, failed
    """

    if is_nan(value) or (isinstance(value, float) and np.isnan(value)):
        return True
    if checker.validation['validate'] == 'length':
        if 'eventid' in checker.name.lower():
            # print(value)
            try:
                uuid.UUID(value)
            except ValueError:
                return False
    if checker.validation['validate'] == 'date' and not(value.__class__ == dt.date(1, 1, 1).__class__):
        return checker.validator.evaluate(value.date())
    elif checker.validation['validate'] == 'integer' or checker.validation['validate'] == 'decimal':
        try:
            num = format_num(value)
        except ValueError:
            num = value
        return checker.validator.evaluate(num)
    else:
        return checker.validator.evaluate(value)


def check_array(data, checker_list, skiprows, config):
    """
    Checks the data according to the validators in the checker_list
    Returns True if the data is good, as well as an empty string

    Parameters
    ---------

    data : numpy ndarray of objects
        The data to be checked.
        The first row should contain the names of the fields as specified in fields.py

    checker_list : dict of Checker objects
        This is a list of the possible checkers made by make_valid_dict

    skiprows: int
        The number of rows skipped when reading in the data with pandas
        If something else is used this should be 1 less, as pandas skips one row
        This is needed to give the excel reference correct

    config: yaml config
        The yaml configuration for the file.

    Returns
    ---------

    good : Boolean
        A boolean specifying if the data passed the checks (True)

    errors: list of strings
        A string per error, describing where the error was found
        On the form: paramName: disp_name : row
    """
    good = True
    errors = []

    # Check that all the required columns are there
    can_miss = True
    if config['name'] == 'aen':
        try:
            evID = np.where(data[0, :] == 'eventID')[0][0]
            pID = np.where(data[0, :] == 'parentEventID')[0][0]
            # If there are no samples without parent IDs we allow inherited values to be missing
            for row in range(1, data.shape[0]):
                if not(is_nan(data[row, evID])) and is_nan(data[row, pID]):
                    # We have a line with ID but not a parent, we stop here
                    can_miss = False
                    break
        except IndexError:
            # Either eventID or parentEventID is missing
            # We are continuing as we know that there are missing columns
            good = False

    required = config['required'][:]

    for req in required:
        if not(req in checker_list):
            inherit = False
        else:
            inherit = checker_list[req].inherit
        if not(req in data[0, :]) and not(can_miss and inherit):
            # print("Missing "+req)
            good = False
            if config['name'] == 'aen':
                errors.append(
                    "Missing required column (parent UUIDs missing?): " + req)
            else:
                errors.append(
                    'Missing required column: ' + req)

    if not(good):
        errors.append(
            "Missing required column(s), not doing any more tests until fixed")
        return good, errors

    # Check that every cell is correct
    try:
        gear = np.where(data[0, :] == 'gearType')[0][0]
    except IndexError:
        gear = None

    if config['name'] == 'aen':
        # Check that parent and event are not the same uuid
        sim = []
        for row in range(1, data.shape[0]):
            if data[row, evID] == data[row, pID]:
                sim.append(row+skiprows+2)
        if sim != []:
            good = False
            errors.append(to_ranges_str(sim) +
                          ' Error: eventID (sampleID) is the same as parent ID')

    for col in range(data.shape[1]):
        if is_nan(data[0, col]):
            continue
        # print(data[0,col])
        try:
            checker = checker_list[data[0, col]]
        except KeyError:
            good = False
            errors.append(
                "Column name not known, Row: 3, value: " + str(data[0, col]))
            continue
        rows = []
        missing = []
        mis = []  # For ones that can't be inherited
        req = checker.name in required
        # Checking type
        for row in range(1, data.shape[0]):
            if not(check_value(data[row, col], checker)):
                if good:
                    errors.append("Content errors")
                good = False
                rows.append(row+skiprows+2)
            if config['name'] == 'aen' and req and (is_nan(data[row, col]) or data[row, col] == ''):
                if not(is_nan(data[row, evID])):
                    if checker.inherit:
                        if is_nan(data[row, pID]):
                            missing.append(row+skiprows+2)
                    else:
                        if is_nan(data[row, pID]):
                                    # Gear doesn't need to have sampleType and location
                            if (checker.name == "sampleType" or checker.name == "sampleLocation") and gear is not None:
                                if is_nan(data[row, gear]):
                                    # print("Here")
                                    missing.append(row+skiprows+2)
                                    continue
                                else:
                                    continue
                        if checker.name != 'parentEventID' and 'remarks' not in checker.name.lower():
                            mis.append(row+skiprows+2)
        if rows != []:
            # print("Testing", rows)
            errors.append(checker.disp_name + ' ('+checker.name + ')'+", Rows: " +
                          to_ranges_str(rows) + ' Error: Content in wrong format')
        if missing != []:
            good = False
            errors.append(checker.disp_name + ' ('+checker.name + ')'+", Rows: " +
                          to_ranges_str(missing) + ' Error: Required value missing (parent UUID missing?)')
        if mis != []:
            good = False
            errors.append(checker.disp_name + ' ('+checker.name + ')' +
                          ", Rows: " + to_ranges_str(mis) + ' Error: Required value missing')

    # Check that the uuids in eventID are unique
    if 'eventID' in data[0, :]:
        index = np.where(data[0, :] == 'eventID')[0][0]
        ind = pd.Index(data[1:, index].astype(np.str))
        if ind.has_duplicates:
            # We have found dupes
            dups = ind[ind.duplicated()].unique()
            #dups = ind.get_duplicates()
            first = True
            for dup in dups:
                if not(is_nan(dup)):
                    if first:
                        first = False
                        errors.append('Duplicate uuids in eventID (sampleID)')
                    errors.append(
                        "Rows: "+to_ranges_str((ind.get_indexer_for([dup])+skiprows+3).tolist()) + ', UUID: '+dup)
                    good = False

    return good, errors


def check_meta(metadata, checker_list, skipcols=1):
    """
    Checks the data according to the validators in the checker_list
    Returns True if the data is good, as well as an empty string

    Parameters
    ---------

    metadata : numpy ndarray of objects
        The metadata to be checked.
        The first column should contain the names of the fields as specified in fields.py

    checker_list : dict of Checker objects
        This is a list of the possible checkers made by make_valid_dict

    skipcols: int, optional
        The number of columns skipped when reading in the data with pandas
        This is needed to give the excel reference correct

    Returns
    ---------

    good : Boolean
        A boolean specifying if the data passed the checks (True)

    errors: list of strings
        A string per error, describing where the error was found
        On the form: paramName: disp_name : row
    """
    good = True
    errors = []
    for row in range(metadata.shape[0]):
        if is_nan(metadata[row, 0]):
            continue
        # print(metadata[0,col])
        try:
            checker = checker_list[metadata[row, 0]]
        except KeyError:
            good = False
            errors.append("Metadata sheet: Column name not known, Row: " +
                          str(row)+", value: " + str(metadata[row, 0]))
            continue
        if metadata.shape[1] < 2 or is_nan(metadata[row, 1]):
            good = False
            errors.append("Metadata sheet: Content missing, Cell: " +
                          xl.utility.xl_rowcol_to_cell(row, 1+skipcols))

    return good, errors


def to_ranges_str(lis):
    """
    Conversion of a list for integers to a string containing ranges.
    For instance [1, 2, 3, 4] will be returned as the string [1 - 4]

    Parameters
    ---------

    lis: list of ints
        The list to be converted

    Returns
    ---------

    out: string
        The resulting string with ranges for sequences consisting of more than
        two steps. Enclosed in swuare ([]) brackets
    """

    out = '['+str(lis[0])
    if len(lis) == 2:
        out = out + ', ' + str(lis[1])
    elif len(lis) > 2:
        first = lis[0]
        prev = first
        ii = 1
        for l in lis[1:]:

            if l == prev+1:
                prev = l
                ii = ii+1
            else:
                # longer step
                if ii > 2:
                    out = out + ' - ' + str(prev)
                # else:
                    # out = out +', '+str(prev)
                prev = l
                first = l
                out = out + ', ' + str(first)
                ii = 0
        if ii > 2:
            out = out + ' - ' + str(prev)
        # else:
            # out = out +', '+str(prev)

    out = out + ']'
    return out


#    sheet = workbook.add_worksheet('Metadata')

#    metadata_fields = ['title', 'abstract', 'pi_name', 'pi_email', 'pi_institution',
#                       'pi_address', 'recordedBy', 'projectID']


def prune(data):
    """
    Remove columns without the identifier (first row) as these are non standard rows

    Parameters
    ---------

    data: numpy ndarray of objects
        The data to be pruned.


    Returns
    ---------

    data: numpy ndarray of objects
        The pruned data
    """

    # print(data[0,:])
    re_ind = []
    for col in range(data.shape[1]):
        name = data[0, col]
        # Remove columns without name:
        if is_nan(name) or name == '':
            re_ind.append(col)

    return np.delete(data, re_ind, axis=1)


def clean(data):
    """
    Goes through the array and cleans up the data
    Fixes some numbers that have not been converted correctly
    Converts uuids to lower and makes sure seperator is '-' and not '+' '/'

    Parameters
    ---------

    data: nunpy ndarray of objects
        The data to be cleaned, first row should be the header row

    Returns
    ---------

    cleaned_data: numpy ndarray of objects
        The cleaned data

    """
    cleaned_data = np.copy(data)
    for col in range(data.shape[1]):
        name = data[0, col]
        for row in range(1, data.shape[0]):
            if not(is_nan(data[row, col])) and 'eventid' in str(name).lower():
                cleaned_data[row, col] = data[row, col].replace(
                    '+', '-').replace('/', '-')
            else:
                try:
                    num = format_num(data[row, col])
                    cleaned_data[row, col] = num
                except ValueError:
                    continue

    return cleaned_data


def run(fname, return_data=False, setup='aen'):
    """
    Method for running the checker on the given input.
    If importing in another program, this should be called instead of the main
    function
    Can be used to return the data as well

    Parameters
    ---------

    fname: string or file like object
        The file to be checked. Can be anything the pandas read_excel method
        excepts (string url, file like object,...)

    return_data: Boolean
        Should the data and metadata be returned
        Default: False

    setup: str
        type of setup to check against.
        Has to be one of the ones in the config.yaml file
        Default: aen

    Returns
    ---------

    good: Boolean
        The result.
        True: pass
        False: fail

    errors: string
        String specifying where the errors were found

    data: pandas array
        Optional, only when return_data is True
        The data in array form.
        First row contains the column names

    metadata: pandas array
        Optional, only when return_data is True
        The metadata in array form
        The first column contains the names
        The second the values
    """

    cores = yaml.full_load(
        open(os.path.join(aen_config_dir, 'config', 'config.yaml'), encoding='utf-8'))['cores']
    for core in cores:
        if core['name'] == setup:
            config = core['sheets'][0]

    checker_list = make_valid_dict()
    # Read in data and prune of custom columns
    skiprows = 1
    try:
        data = prune(xlsx_to_array(fname, skiprows=1))
        data = clean(data)
    except XLRDError:
        return False, ["Does not contain the 'Data' sheet. Is this the correct file?"]
    # Check the data array
    good, error = check_array(data, checker_list, skiprows, config)

    # Check if we should look for the metadata sheet
    if 'extrasheet' in config and 'metadata' in config['extrasheet']:
        # Read in metadata and check it
        try:
            if isinstance(fname, io.BytesIO):
                fname.seek(0)
            metadata = xlsx_to_array(
                fname, sheetname="Metadata", skiprows=None, header=None)
            # print(metadata[:,1])
        except XLRDError:
            return False, ["Does not contain the 'Metadata' sheet. Is this the correct file?"]

        g, e = check_meta(metadata[:, 1:3], checker_list)

        good = good and g
        for it in e:
            error.append(it)

    if return_data:
        return good, error, data, metadata[:, 1:3]
    else:
        return good, error


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''
    try:
        args = parse_options()
        infile = args.input
    #         save_pages(output, N=args.n)
        good, error = run(infile, setup=arg.type)
        if good:
            print('''
                  Your file has passed the checker!
                  
                  Please note that there are several things that have not been checked. Please ensure that each row in your sample log matches what is written on the physical sample labels.
                  
                  Human error is the biggest cause of mismatches between the sample logs and the physical sample labels. Please in particular check that any of these common errors have not been made. They are much more difficult to fix after the cruise has finished.
                  
                  1. Printing new sample labels and forgetting to re-scan them.
                  2. Copy-paste errors.
                  3. After printing labels, the information is preserved on the label printing page. Sometimes people forget to make all the necessary changes when printing new labels.
                    
                  Thanks for your efforts.
                    
                  Takk for hjelpe!
                  ''')
        else:
            print("Errors found. They were:")
            for line in error:
                print(line)

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0


def parse_options():
    """
    Parse the command line options and return these. Also performs some basic
    sanity checks, like checking number of arguments.
    """
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

    Created by Pål Ellingsen on %s.

    Distributed on an "AS IS" basis without warranties
    or conditions of any kind, either express or implied.

    USAGE
''' % (program_shortdesc, str(__date__))

    # Setup argument parser
    parser = ArgumentParser(description=program_license,
                            formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("input", type=str,
                        help="The input xlsx file to check")
    parser.add_argument('-t', "type", type=str, default='aen',
                        help="The type of input file, [aen or darwin], Default: aen ")
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)

    # Process arguments
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    sys.exit(main())
