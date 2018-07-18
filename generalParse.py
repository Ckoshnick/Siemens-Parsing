# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:46:24 2018

@author: koshnick
"""

import pandas as pd
import mypy
import os


# =============================================================================
#
# =============================================================================

def license_parse(section):
    # take all lines after license and add them to the same line as a single
    # item
    startLine = 0

    for i, line in enumerate(section):
        if line.find("License(s):") == 0:
            startLine = i

    if startLine == 0:
        return section
    else:
        length = len(section)
        combineRows = section[startLine+1:length]
        combineString = '\n'.join(combineRows).replace(','," ")

        section[startLine] = 'License(s):,' + combineString

        #Drop the rest of the rows

        section = section[0:startLine+1]

        return section

def services_parse(section):
    # find services support and add all text up until license line to a single
    # line

    startLine = 0
    lastLine = len(section)

    for i, line in enumerate(section):
        if line.find("Services Supported,Enabled") == 0:
            startLine = i
        if line.find('License(s):') == 0:
            lastLine = i - 1

    if startLine == 0:
        return section
    else:
        if lastLine == len(section):
#            print(section)
            print('no license')

        length = len(section)
        combineRows = section[startLine+1:lastLine]
        combineString = '\n'.join(combineRows).replace(','," ")

        section[startLine] = "Services Supported Enabled," + combineString

        section = section[0:startLine+1] + section[lastLine+1:length]

    return section

def DNS_parse(section):
    # add a single integet to the DNS address line so they are unique
    j = 1

    for i, line in enumerate(section):
        if line.find('DNS Address:') == 0:
            line = line.replace('DNS Address:','DNS Address {}:'.format(j))
            section[i] = line
            j += 1

    return section


def clean_section(section):
    ## aggregation of functions that need to be applied to this data set to fit
    # the dominant mold

    # license parse last
    section = DNS_parse(section)
    section = services_parse(section)
    section = license_parse(section)

    return section


# =============================================================================
#
# =============================================================================

def parse_file(fileName, heading, spacing=1):

    # Initial Parse to populate fields
    # Extra formatting?
    # Second parse to populate fields/values


    with open(fileName, 'r') as f:
        data = f.readlines()

    # Remove " and \n charachters from file
    for j, line in enumerate(data):
        temp = line.replace('"', '')
        data[j] = temp.replace('\n', '')

    # Build index of headings
    sectionStart = []
    for i, line in enumerate(data):
        if i == 0:
            # Start -1 in section list if first line if file is part of report
            if line.split(',')[0] == 'Date:':
                sectionStart.append(0)

        if line.find(heading) == 0:
            sectionStart.append(i)

    # 3 slice into many parts
    sections = []
    for i, index in enumerate(sectionStart[0:len(sectionStart)-1]):
        section = data[index:sectionStart[i+1] - spacing]

        if len(section) > 1:
            section = clean_section(section)
            sections.append(section)
        else:
            failList.append([index, data[index]])

    # 4 parse each section
    bigDict = {}
    uniqueID = 0
    for section in sections:
        uniqueID += 1
        collector = {}

        for i, line in enumerate(section):
            maxLength = len(section)
            splitLine = line.split(',')

            if splitLine == ['']:
                continue

            try:
                collector[splitLine[0]] = splitLine[1]
            except IndexError:
                print('index error')
                print(splitLine)
                pass

        # combine section into bigDict which is later fed into pd.DataFrame()
        bigDict[uniqueID] = collector


    # 5 Combine into single df
    data = pd.DataFrame(bigDict).T

#    # re-order columns alphabetically
    cols = data.columns.sort_values()
    data = data[cols]

    return data


# =============================================================================
#
# =============================================================================

fileName = 'UCD_PanelConfigRpt_APG1_20180702_0958.csv'
parsed = parse_file(fileName,'Panel System Name:')

parsed.to_csv('parsed {}'.format(fileName))

