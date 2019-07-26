#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: dumps the client list from glass for a specific region iinto a CSV format

Usage:
    $ python  getclients [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           getclients
    @version        0.4.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 0.40
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import os
import re
import sys
import requests
import pandas

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This is designed as a sample converter of json files to csv format.
It will keep the source and the destination file

""")

PARSER.add_argument('-l', metavar='<site>', dest='sitename', help='glass site')
PARSER.add_argument('-u', metavar='<user>', dest='username', help='specify username')
PARSER.add_argument('-p', metavar='<pass>', dest='password', help='specify password')
PARSER.add_argument('-o', metavar='<file>', dest='outputfile', help='specify outputfile')

ARGS = PARSER.parse_args()

SITENAME = ARGS.sitename
BASEURL = 'https://%s-monitor.sumologic.net/glass' % SITENAME
JSONURL = '%s/api/json/datastore/searchable/exportjson' % BASEURL
MYQUERY = '%s/organizations' % JSONURL

if ARGS.username:
    os.environ["GLASSUSER"] = ARGS.username
if ARGS.password:
    os.environ["GLASSPASS"] = ARGS.password

try:
    GLASSPASS = os.environ['GLASSPASS']
    GLASSUSER = os.environ['GLASSUSER']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

def main():
    """
    This is to dump the glass client list for a given region
    It filter out the system and automation accounts
    """
    getclients()

def getclients():
    """
    make a connection to the web interface, pull down information as a JSON payload
    then convert the JSON payload into a CSV using pandas and cleanup/filter data
    """

    results = requests.get(MYQUERY, auth=(GLASSUSER, GLASSPASS))
    if 'content-length' in results.headers:
        jsonlength = int(results.headers['content-length'])
    else:
        jsonlength = len(results.text)

    if results.status_code == 200:
        if jsonlength > 22:
            dataframe = pandas.read_json(results.text)
            dataframe.to_csv()
            o_f = dataframe.loc[:, ['accountType', 'id', 'displayName']]
            o_f['sitename'] = SITENAME
            r_1 = re.compile(r'(,|\.|\s+|@|\&)', flags=re.IGNORECASE)
            r_2 = re.compile(r'_+', flags=re.IGNORECASE)
            r_3 = re.compile(r'_$', flags=re.IGNORECASE)
            o_f['accountType'] = o_f.accountType.str.lower()
            o_f['accountType'] = o_f.accountType.str.replace(r_1, '_', regex=True)
            o_f['accountType'] = o_f.accountType.str.replace(r_2, '_', regex=True)
            o_f['accountType'] = o_f.accountType.str.replace(r_3, '', regex=True)
            o_f['displayName'] = o_f.displayName.str.lower()
            o_f['displayName'] = o_f.displayName.str.replace(r_1, '_', regex=True)
            o_f['displayName'] = o_f.displayName.str.replace(r_2, '_', regex=True)
            o_f['displayName'] = o_f.displayName.str.replace(r_3, '', regex=True)
            g_f = o_f[~o_f.displayName.str.contains(r'automation|sumologic.com')]
            outcolumns = ['id', 'sitename', 'accountType', 'displayName']
            csvout = g_f.to_csv(columns=outcolumns, index=False, header=False)
            if ARGS.outputfile:
                outputobj = open(ARGS.outputfile, "w+")
                outputobj.write(csvout)
                outputobj.close()
            else:
                print(csvout, end='')
        else:
            print('Site: {} Small_Payload: {}'.format(SITENAME, jsonlength))
    else:
        print('Error: {} OrgId: {}'.format(results.status_code, SITENAME))

if __name__ == '__main__':
    main()
