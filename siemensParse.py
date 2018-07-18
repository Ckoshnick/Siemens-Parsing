# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 11:42:39 2018

@author: koshnick
"""

import pandas as pd
import mypy
import os


def parseFile(fileName, tags, tagOrder, seperator=' ***'):
    # 1 open file
    # 2 Build index of all seperators
    # 3 slice into many parts
    # 4 parse each section
    # 5 combine into single df
    # 6 output

    # Initial Vars
    # Start -1 in section list if first line if file is part of report
    sectionStart, sections, failList = [], [], []

    # 1 open file
    with open(fileName, 'r') as f:
        data = f.readlines()

    # Remove " and \n charachters from file
    for j, line in enumerate(data):
        temp = line.replace('"', '')
        data[j] = temp.replace('\n', '')

    # 2 Build index of all seperators
    for i, line in enumerate(data):
        if i == 0:
            # Start -1 in section list if first line if file is part of report
            if line.split(',')[0] == 'Date:':
                sectionStart.append(-1)

        if line.find(seperator) == 0:
            sectionStart.append(i)

    # 3 slice into many parts
    for i, index in enumerate(sectionStart[0:len(sectionStart)-1]):
        section = data[index+1:sectionStart[i+1]]

        if len(section) > 1:
            sections.append(section)
        else:
            failList.append([index, data[index]])

    # 4 parse each section
    bigDict = {}

    actionStop = ['Comment:', 'Type:', 'Revision:']
    commentStop = ['Type:', 'Revision:', 'Location:']

    uniqueID = 0
    for section in sections:

#        print(section)
        uniqueID += 1
        collector = {}

        for i, line in enumerate(section):

            maxLength = len(section)
            splitLine = line.split(',')

             #Handle the first line of each section sperately due to format
            if splitLine[0] == "Point System Name:":
                collector[splitLine[0]] = splitLine[1]

            if splitLine[0] == "Date:":
                collector[splitLine[0]] = splitLine[1]
                collector[splitLine[3]] = splitLine[4]
                collector[splitLine[6]] = splitLine[7]

            # Ensure the  'Action:' line is appended if it spills over
            if splitLine[0] == 'Action:':
                actionString = line[len('Action:')+1:]
                j = 0

                while True:
                    j += 1
                    # Allows comment section to be last field in section
                    if j + i == maxLength:
                        break
                    # Stop builing action text if next field reached
                    if section[i+j].split(',')[0] in actionStop:
                        break
                    else:
                        actionString += section[i+j]

                collector['Action:'] = actionString.rstrip(',')
                continue

            # Ensure the 'Comment:' line is appended if it spills over
            if splitLine[0] == 'Comment:':
                commentString = line[len('Comment:')+1:]
                j = 0

                while True:
                    j += 1
                    # Allows Action section to be last field in section
                    if j + i == maxLength:
                        break
                    # Stop builing comment text if next field reached
                    if section[i+j].split(',')[0] in commentStop:
                        break
                    else:
                        commentString += section[i+j]

                collector['Comment:'] = commentString.rstrip(',')
                continue

            # Normal lines
            if splitLine[0] in tags:
                collector[splitLine[0]] = splitLine[1]

        # combine section into bigDict which is later fed into pd.DataFrame()
        bigDict[uniqueID] = collector

    # 5 Combine into single df
    data = pd.DataFrame(bigDict).T

    # re-order columns
    columns = []
    # Handle sorting columns even if some columns are missing
    for col in tagOrder:
        if col in data.columns:
            columns.append(col)

    data = data[columns]

    # This line will sort by name to aggregate entries for the same system
#    data.sort(columns = 'System Name:', inplace=True)

    return data


def multiple_files():
    csvList = mypy.find_files(filePath = os.path.dirname(os.path.realpath(__file__)))
    for fileName in csvList:
        data = parseFile(fileName, tags=tags)
        # Save output to file "Parsed + input file name"
        data.to_csv('Parsed ' + fileName)


def single_file(fileName, tags, tagOrder):
    data = parseFile(fileName, tags, tagOrder)
    # Save output to file "Parsed + input file name"
    data.to_csv('Parsed ' + fileName)


tags = ['Name:',
        'Point Name:',
        'System Name:',
        'Operator:',
        'Point Type:',
        'Revision:',
        'Location:',
        'Value:',
        'Priority:',
        'Action:',
        'Comment:',
        'Reason for Change:',
        'Property:',
        'Before:',
        'After:']

tagOrder = ['Date:',
            'Time:',
            'Point Name:',
            'System Name:',
            'Name:',
            'Point Type:',
            'Operator:',
            'Priority:',
            'Value:',
            'Seq Number:',
            'Revision:',
            'Action:',
            'Property:',
            'Before:',
            'After:',
            'Reason for Change:',
            'Location:',
            'Comment:']

#tags = ['Supervised:',
#        'Revision Number:',
#        'Trend Every:',
#        'Samples at Panel:',
#        'Collection Enabled:',
#        'Auto Collection:',
#        'Max Samples at PC:',
#        'Trend On Event:',
#        'Descriptor:']

#tagOrder = ["Point System Name:",
#            'Descriptor:',
#            'Trend Every:',
#            'Collection Enabled:',
#            'Auto Collection:',
#            'Samples at Panel:',
#            'Max Samples at PC:',
#            'Trend On Event:',
#            'Supervised:',
#            'Revision Number:']


single_file('DatabaseMods7_07-17-18_07-03.csv', tags, tagOrder)
#multiple_files()