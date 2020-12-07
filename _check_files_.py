#!/usr/bin/python3

# file: _check_files_.py
# this is a python script
# created on 2020-12-06 by Alexander Stohr, Lindau, GERMANY
# for scrumpypoker/i18n verification
# see also: https://github.com/scrumpypoker/i18n.git

# ==== imports
import os
import sys
import re


# ==== constants
def separator() -> str:
    return '": "'


# ==== functions

# helper function for sort/sorted
def get_key_column (line):
    return line[0]

# take a 2D list array and check if the given value equals the value in the given column from data
def find_key_in_list(key, data, column = 0):
    for line in data:
        if key == line[column]:
            return data.index(line)
    return -1

def check_list_for_duplicates(data, column = 0):

    for line in data:
        key = line[column]
        this_line = data.index(line)
        first_line = find_key_in_list(key, data, column)
        if (this_line != first_line):
            print ('ERROR: key "' + key + '" already exists (' +str(this_line) + ',' + str(first_line) + ')[' + str(line_id) + ')')

def read_file (file_name : str) -> dict:
    print ('reading file: ' + file_name)
    f = open (file_name, 'r')

    line_id = 0
    eof = False
    trail_chars = 0

    linebreaks = '\r\n\t ' # set of line break & whitespace chars
    #linebreaks = '\r\n' # set of line break chars

    data = [ ] # start with an empty table
    # note: for pre-Python3.7 this is valid: a dictionary might see immediate sorting or re-arranging!

    for line in f:
        # drop all trailing line break & whitespace chars
        while (len(line) > 0):
            if (linebreaks.find(line[-1]) != -1):
                line = line[:-1]
            else:
                break

        verbose_txt = ''
        #verbose_txt = '; line=' + line

        if (line_id == 0):
            # check for bad leading line
            if (line != '{'):
                print ('ERROR: line[' + str(line_id) + '] bad start of file' + verbose_txt)
        else:
            # check for the syntactical end of data
            if (line == '}'):
                if (trail_chars == 2):
                    print ('ERROR: line[' + str(line_id) + '] previous data line had a trailig comma' + verbose_txt)
                if (eof):
                    print ('ERROR: line[' + str(line_id) + '] multiple end markers' + verbose_txt)
                eof = True
            else:
                if (eof):
                    # its some line after the trailing line marker
                    if (line != ''):
                        print ('ERROR: line[' + str(line_id) + '] extra data after body' + verbose_txt)
                else:
                    # its a body line
                    # check for lead in
                    if (line[:3] != '  "'):
                        print ('ERROR: line[' + str(line_id) + '] bad lead in for body line' + verbose_txt)
                    # check for lead out
                    if (line[-2:] == '",'):
                        trail_chars = 2
                    else:
                        if (line[-1:] == '"'):
                            trail_chars = 1
                        else:
                            print ('ERROR: line[' + str(line_id) + '] bad lead out for body line' + verbose_txt)
                    # check body
                    body = line[3:-trail_chars]
                    separator_pos = body.find(separator())
                    if (separator_pos == -1):
                        print ('ERROR: line[' + str(line_id) + '] bad separator for body line' + verbose_txt)
                    else:
                        dummy = 0
                        key = body[:separator_pos]
                        value = body[separator_pos + len(separator()):]
                        if (value.find(separator()) != -1):
                            print ('ERROR: line[' + str(line_id) + '] multiple items per body line' + verbose_txt)
                        #print (key + ':' + value)
                        data.append([key, value])

        line_id += 1

    f.close ()

    check_list_for_duplicates(data, 0)

    # sort table
    data = sorted(data, key=get_key_column)

    # write sorted file
    f = open (file_name + '.sorted', 'w')
    f.write ('{\n')
    id = 0
    for line in data:
        if (id > 0):
            f.write(',\n') # terminate the previous line with a comma
        f.write ('  "' + line[0] + '": "' + line[1] + '"')
        id += 1
    f.write('\n') # terminate the previous line without a comma
    f.write ('}')
    f.close

    return data

def compare_file (file_name : str, ref_data : dict):
    data = read_file (file_name)

    # check for any key in 'ref_data' also occures in 'data'
    prev_key = '<start>'
    prev_data_line = -1

    for key, value in ref_data:
        data_line = find_key_in_list (key, data, 0)
        if (data_line == -1):
            print ('ERROR: key "' + key + '" is missing from data file - insert the next line after key-line for "' + prev_key + '"')
            print ('  "' + key + separator() + value + '",')
        else:
            if (prev_data_line + 1 != data_line):
                print ('ERROR: key "' + key + '" is in bad order according to the reference (' + str(prev_data_line) + ',' + str(data_line) + ') - it should be after "' + prev_key + '"')
            prev_data_line = data_line
        prev_key = key

    # check for any key in 'data' also occuring in 'ref_data'
    for key, value in data:
        data_line = find_key_in_list (key, ref_data, 0)
        if (data_line == -1):
            print ('ERROR: key "' + key + '" is missing from reference file - you should remove it!')


# ==== main
print ('python version = ' + sys.version)
print ('note: line numbers are indexed for this check with a start at "0" - please add "1" for regular text editors')
print ('doing file check...')

# read the master file
data_ref = read_file ('en_US.json')
if (1 == 0):
    for key, value in data_ref:
        print (key)
    exit (0)

# read and check the derived files
compare_file ('bg_BG.json', data_ref)
compare_file ('nl_NL.json', data_ref)
compare_file ('pt_BR.json', data_ref)

compare_file ('by_BY_PR3.json', data_ref)
compare_file ('de_DE_PR5.json', data_ref)
compare_file ('de_DE_PR7.json', data_ref)
compare_file ('es_AR_PR8.json', data_ref)

print ('done.')

# ### EOF ###
