#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: this script collects Sumo Logic clients from Glass

Usage:
    $ python step_001_listclients [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           step_001_listclients
    @version        1.0.0
    @author-name    Wayne Kirk Schmidt
    @author-email   wayne.kirk.schmidt@gmail.com
    @license-name   APACHE 2.0
    @license-url    http://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = 1.00
__author__ = "Wayne Kirk Schmidt (wayne.kirk.schmidt@gmail.com)"

import argparse
import os
import re
import sys
import requests
import pandas

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This downloads a list of clients by deployment, as a config for later stages

""")

PARSER.add_argument('-u', metavar='<user>', dest='username', help='specify username')

PARSER.add_argument('-p', metavar='<pass>', dest='password', help='specify password')

PARSER.add_argument('-s', metavar='<site>', default='all', dest='sitename', help='glass site')

PARSER.add_argument('-d', metavar='<dumpdir>', default='/var/tmp/glassdump', \
                    dest='dumpdir', help='specify dumpdir')

ARGS = PARSER.parse_args()

SITENAME = ARGS.sitename
GLASSTAG = 'glassdump'
DUMPBASE = ARGS.dumpdir

DEPLOYMENTDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../etc'))
DEPLOYMENTLIST = os.path.join(DEPLOYMENTDIR, 'sitelist.cfg')

if ARGS.username:
    os.environ["GLASSUSER"] = ARGS.username

if ARGS.password:
    os.environ["GLASSPASS"] = ARGS.password

try:
    GLASSPASS = os.environ['GLASSPASS']
    GLASSUSER = os.environ['GLASSUSER']

except KeyError as myerror:
    print(f'Environment Variable Not Set :: {myerror.args[0]}')

def main():
    """
    This loops through a list of deployments
    """

    deploymentlist = []

    if SITENAME == 'all':
        with open(DEPLOYMENTLIST, "r", encoding='utf8') as listobject:
            deploymentlist = listobject.readlines()
    else:
        deploymentlist.append(SITENAME)

    for deployment in deploymentlist:

        deployment = deployment.rstrip()
        baseurl = f'https://{deployment}-monitor.sumologic.net/glass'
        jsonurl = f'{baseurl}/api/json/datastore/searchable/exportjson'
        myquery = f'{jsonurl}/organizations'

        dumpdir = os.path.join(DUMPBASE, 'cfg', deployment )
        os.makedirs(dumpdir, exist_ok = True)

        glassfile = f'{deployment}.csv'
        dumpfile = os.path.join(dumpdir, glassfile)

        glassdump(myquery,deployment,dumpfile)

def glassdump(glassquery,mylocation,outputfile):
    """
    This dumps the file from JSON into CSV to be used later
    """

    results = requests.get(glassquery, auth=(GLASSUSER, GLASSPASS))

    if 'content-length' in results.headers:
        jsonlength = int(results.headers['content-length'])
    else:
        jsonlength = len(results.text)

    if results.status_code == 200:
        if jsonlength > 22:
            dataframe = pandas.read_json(results.text)
            dataframe.to_csv()
            o_f = dataframe.loc[:, ['accountType', 'id', 'displayName']]
            o_f['sitename'] = mylocation
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
            with open(outputfile, "w+", encoding='utf8') as outputobj:
                outputobj.write(csvout)
            print(csvout, end='')
        else:
            print(f'Site: {mylocation} Small_Payload: {jsonlength}')
    else:
        print(f'Error: {results.status_code} OrgId: {mylocation}')

if __name__ == '__main__':
    main()
