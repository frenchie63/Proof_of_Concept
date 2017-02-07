# # PROOF OF CONCEPT
#
# # Description: Count the number of drilling events and rank the well depending of drilling events score
# # Create dictionnary of drilling events , and well dataframe


from pandas import Series, DataFrame
import subprocess
import numpy as np
from fnmatch import fnmatch, fnmatchcase
import pandas as pd

print '\n'
path = raw_input('Please enter the path of your end of well report, in a text file format:')
print '\n'


wellDF = DataFrame(columns=['WellName', 'Northing', 'Easting', 'Basin', 'Main Drilling Event', 'Score'])

# Create a dictionnary with the different key names and their point
drilling_events = {'blowout': -80,
                   'pressure kick': -20,
                   'major losses': -20,
                   'pack off': -10,
                   'stuck pipe': -10,
                   'sidetrack': -30,
                   'tight spot': -10,
                   'formation integrity test': 10,
                   'fit': 10,
                   'reaming': 10,
                   'leak off test': 30,
                   'lot': 30}

# # Import Text File
words = []

with open(path) as fl:
    for lines in fl:
        lines = lines.strip().split('\n')
        for l in lines:
            words.append(l.lower())

# Place Well name, easting, northing into DataFrame

# Find the indexes for  well name, the drilled basin and its location
# By using find, we can get the results with additional typo or punctuation on the side


for i, j in enumerate(words):
    if fnmatch(j, 'easting*') == True:
        locationx = i
    elif fnmatch(j, 'northing*') == True:
        locationy = i
    elif fnmatch(j, 'basin*') == True:
        locationbasin = i
    elif fnmatch(j, 'well name') == True:
        locationname = i

locationx, locationy, locationbasin, locationname

# Populating table with well name, easting and northing

wellDF['WellName'] = [(words[locationname + 2])]
wellDF['Easting'] = [(words[locationx + 2]).strip('me')]
wellDF['Northing'] = [(words[locationy + 2]).strip('mn')]
wellDF['Basin'] = [words[locationbasin + 2]]

# # Creating DF events with the drilling events encountered

# # 1. Isolate the operations summary, transform to list and count drilling events

# Splitting information per space for Operations Summary

for i, j in enumerate(words):
    if j == '1 operations summary':
        start = i
    elif j.find('drilling summary') != -1:
        start = i
    elif j.find('casing') != -1:
        end = i

# Create new list with operations summary as words instead of sentences

operation = words[start:end]

summary = []

for op in operation:
    lines = op.split()
    for l in lines:
        summary.append(l)


# function to count the drilling events in the operation summary

def dr_events(eowr):
    counts = dict()
    for w in eowr:
        if w in drilling_events.keys():
            counts[w] = counts.get(w, 0) + 1

    return counts


# apply function to operation summary (as a list of words)
# dr is your dictionnary holding your drilling events (keys) and their occurence (values)
dr = dr_events(summary)


# new function to count the drilling events in two or three words

def dr_2_events(eowr, dr_dictionnary):
    twowords_dr = ['tight spot', 'stuck pipe', 'formation integrity test', 'pack off', 'major losses', 'leaf off test']
    twowords_dr_list = []

    for ev in twowords_dr:  # build a list of list, as we want to take the first element
        word = ev.split()
        twowords_dr_list.append(word)

    mydict = {}
    for i, j in enumerate(summary):
        for w in twowords_dr_list:
            if j.find(w[0]) != -1:  # take the first element of the list
                if summary[i + 1].find(w[1]) != -1:  # check the second element
                    mydict[' '.join(w)] = mydict.get(' '.join(w), 0) + 1

    final_drDict = dict(mydict.items() + dr_dictionnary.items())  # merge the two dictionnaries into one

    return final_drDict


dr = dr_2_events(summary, dr)

# # 2. Insert drilling events into events DF and complete wellDF with main drilling event and score

# Directly input key and values from drilling events dictionnary dr

events = DataFrame.from_dict(dr, orient='index').reset_index().rename(columns={0: 'Occurence',
                                                                               'index': 'Drilling Event'})

# Map the value attributed to each drilling event into score column and compute the total

events['Score'] = events['Drilling Event'].map(drilling_events)

events['Final'] = events['Occurence'] * events['Score']

# Add the final Score to well dataframe amd most encountered drilling event

wellDF['Score'] = events['Final'].sum()
wellDF['Main Drilling Event'] = events['Drilling Event'][events['Occurence'].idxmax()]

print 'Here is the information extracted from the end of well report:'
print wellDF

wellDF.to_csv(path_or_buf='C:\Data\Proof_of_concept\welldatabase.csv', sep=',', na_rep='',
                   float_format=None, columns=None, header=True, index=False,
                   index_label=None, mode='w', encoding=None, compression=None,
                   quoting=None, quotechar='"', line_terminator='\n', chunksize=None,
                   tupleize_cols=False, date_format=None, doublequote=True, escapechar=None, decimal='.')



