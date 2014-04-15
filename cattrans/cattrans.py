#!/usr/bin/python3

import re
import copy
import pprint
import datetime
from datetime import date

file_name = '/home/derek/Downloads/TYEDRV04-20140215.csv'
fields = {'Date':0,'Description':1,'Value':2,'Hit':3}

def datetostr(date_val):
    dl = list(map(int,date_val))
    dt = date(dl[2],dl[1],dl[0])
    month = dt.strftime("%B %Y")
    return month

# process the relevant categories to lookup
category_results = {'Total':1,'Unknown':[]}
category_lookup = {'Train':['XCOUNTRY'],
                   'Petrol':['PETROL']}

for category in category_lookup:
    category_results[category] = []

# read in the transactions file into the trans list
# (removing the header and any blank lines)
# TODO Check that this picks up every transaction
trans = []
pattern = """
          ^([\d/]{10}),           # date in format 01/01/2014
          .{3},\"(.*?)\",         # description (following transaction type field)
          (-?\d{1,5}\.\d{2})      # value (e.g. 1234.01)
          """

for line in open(file_name):
	field_values = re.search(pattern,line,re.VERBOSE)
	if field_values:
		trans.append(field_values.groups())

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
    
    for category in category_lookup:
        for lookup in category_lookup[category]:
            if re.search(lookup,tran[fields['Description']]):
                month_dict[month][category].append(float(tran[fields['Value']][1:]))

def lookup_hit(transaction):
    for category in category_lookup:
        for lookup in category_lookup[category]:
            if re.search(lookup,tran[fields['Description']]):
                return [category, float(tran[fields['Value']][1:])]

    return false

# loop through the remaining transactions again and mark them as unknown
for tran in trans:
    # determine the month that this transaction belongs to
    month = datetostr(tran[fields['Date']].split('/'))
    month_dict[month]['Unknown'].append(float(tran[fields['Value']][1:]))

# PRINT THE RESULTS

# string representation of a datetime object (so they can be sorted chronolgically)
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
