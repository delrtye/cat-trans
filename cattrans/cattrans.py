#!/usr/bin/python3

import sys
import re
import copy
import pprint
import datetime
from datetime import date

cats_file = sys.argv[1]
trans_file = sys.argv[2]

# process the relevant categories to lookup
category_results = {'Total':1,'Unknown':[],'CASH':[],'BILL':[],'CREDIT':[]}
category_lookup = dict()

for line in open(cats_file):
    field_values = re.split(',',line.rstrip())
    category_lookup[field_values[0]] = field_values[1:]

for category in category_lookup:
    category_results[category] = []

def datetostr(date_val):
    dl = list(map(int,date_val))
    dt = date(dl[2],dl[1],dl[0])
    month = dt.strftime("%B %Y")
    return month

def lookup_hit(transaction):
    for category in category_lookup:
        for lookup in category_lookup[category]:
            if re.search(lookup,tran[fields['Description']]):
                return [category, float(tran[fields['Value']][1:])]
    return false
    
# read in the transactions file into the trans list based on pattern that
# identifies date, description and value fields - add additional 'hit' field
# and set it to 0 (no hit)
trans = []
fields = {'Date':0,'Type':1,'Description':2,'Value':3,'Hit':4}
pattern = """
          ^([\d/]{10}),           # date in format 01/01/2014
          (.{3}),                 # type (e.g. POS D/D C/L)
          \"(.*?)\",              # description 
          (-?\d{1,5}\.\d{2})      # value (e.g. 1234.01)
          """

for line in open(trans_file):
	field_values = re.search(pattern,line,re.VERBOSE)
	if field_values:
            trans.append(list(field_values.groups() + (0,)))

# loop through each transaction and create dictionaries (one for each month)
month_dict = dict()

for tran in trans:
    # determine the month that this transaction belongs to
    month = datetostr(tran[fields['Date']].split('/'))

    # check if the month dictionary exists - if not make a deepcopy
    # of the transaction categories dictionary into it (this is a sub dict)
    if month in month_dict:
       month_dict[month]['Total'] += 1
    else:
       month_dict[month] = copy.deepcopy(category_results)
   
    # check if this is a cash withdrawal or direct debit
    if tran[fields['Type']] == 'C/L':
        month_dict[month]['CASH'].append(float(tran[fields['Value']][1:]))
        tran[fields['Hit']] = 1

    elif (tran[fields['Type']] == 'D/D') or (tran[fields['Type']] == 'S/O'):
        month_dict[month]['BILL'].append(float(tran[fields['Value']][1:]))
        tran[fields['Hit']] = 1

    elif tran[fields['Type']] == 'BAC': 
        month_dict[month]['CREDIT'].append(float(tran[fields['Value']])) # no minus so don't slice
        tran[fields['Hit']] = 1

    else:
        # for each category loop through its lookup values and compare them against
        # the description
        for category in category_lookup:
            for lookup in category_lookup[category]:
                if re.search(lookup,tran[fields['Description']]):
                    month_dict[month][category].append(float(tran[fields['Value']][1:]))
                    tran[fields['Hit']] = 1

# loop through the transactions, which didn't hit and mark them as unknown
for tran in trans:
    if tran[fields['Hit']] == 0:
        # determine the month that this transaction belongs to
        month = datetostr(tran[fields['Date']].split('/'))
        month_dict[month]['Unknown'].append(float(tran[fields['Value']][1:]))

# PRINT THE RESULTS

# string representation of a datetime object (so they can be sorted chronologically)
dlist = list(map(lambda a: str(datetime.datetime.strptime(a,'%B %Y')), month_dict))

# loop through the sorted months
print('-'*40)
for month in sorted (dlist):
    
    # convert the month back into its original form (now we know we are in order)
    month = datetostr([1] + month.split('-')[1::-1])

    # Print out the month header (including total transactions for month
    print("{}{} ({})".format(' ' * int((40 - len(month)) / 2 - 1), month.upper(), month_dict[month]['Total']))
    print("{:<20}{:<10}{:<10}{}".format(' ','Total','Average','Count'))

    for category in month_dict[month]:
        # calculate the total and mean average of the transaction values
        if isinstance(month_dict[month][category],list):
            category_total = 0
            category_count = 0
            for value in month_dict[month][category]:
                category_total = round(category_total + value,2)
                category_count += 1
 
            try: 
                print("{:<20}£{:<10}£{:<10}{}".format(category, category_total, round(category_total / category_count,2), category_count))
            except ZeroDivisionError as err:
                print("{:<20}£{:<10}£{:<10}{}".format(category, 0, 0, 0))

    print('-'*40)
