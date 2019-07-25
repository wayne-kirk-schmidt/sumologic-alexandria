#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: dumps a glass file for a specific file into a csv file

Usage:
    $ python  glassdump [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           glassdump
    @version        0.4.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 0.40
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import datetime
import os
import sys
import requests
import pandas

sys.dont_write_bytecode = 1
PARSER = argparse.ArgumentParser(description="""

This pulls down a specific glass file for a given client and location

""")

PARSER.add_argument('-u', metavar='<user>', dest='username', help='set username')
PARSER.add_argument('-p', metavar='<pass>', dest='password', help='set password')
PARSER.add_argument('-l', metavar='<site>', dest='sitename', help='set glass site')
PARSER.add_argument('-c', metavar='<cfgfile>', dest='cfgfile', help='provide config')
PARSER.add_argument('-i', metavar='<id>', dest='orgid', help='set orgid')
PARSER.add_argument('-d', metavar='<dir>', dest='destdir', help='set output dir')
PARSER.add_argument('-g', metavar='<glass>', dest='glassitem', help='specify glass item to get')

ARGS = PARSER.parse_args()

if ARGS.username:
    os.environ["GLASSUSER"] = ARGS.username
if ARGS.password:
    os.environ["GLASSPASS"] = ARGS.password

try:
    GLASSPASS = os.environ['GLASSPASS']
    GLASSUSER = os.environ['GLASSUSER']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

GLASS_DICT = {'rdscq' : 'query'}
GLASS_LIST = list(GLASS_DICT.keys())

def main():
    """
    The script will collect a list of the glass files for a given client
    After doing so, it will write this to a local directory
    """
    sitename = ARGS.sitename
    orgid = ARGS.orgid
    cfgfile = ARGS.cfgfile

    if not cfgfile:
        baseurl = 'https://%s-monitor.sumologic.net/glass' % sitename
        jsonurl = '%s/api/json/datastore/searchable/exportjson' % baseurl
        glassdump(jsonurl, sitename, orgid)
    else:
        with open(cfgfile) as cfgobj:
            for cfgline in cfgobj:
                orgid, sitename, orgtype, orgname = cfgline.split(',')
                baseurl = 'https://%s-monitor.sumologic.net/glass' % sitename
                jsonurl = '%s/api/json/datastore/searchable/exportjson' % baseurl
                glassdump(jsonurl, sitename, orgid)

def glassdump(jsonurl, sitename, orgid):
    """
    make a connection to the web interface, pull down information as a JSON payload
    then convert the JSON payload into a CSV using pandas and cleanup/filter data
    """

    homedir = os.path.abspath((os.environ['HOME']))
    dumpdir = '%s/Downloads/cscontent/output/%s/%s' % (homedir, sitename, orgid)

    os.makedirs(dumpdir, exist_ok=True)

    for glass_item in GLASS_LIST:
        glass_query = '%s/%s?orgid=%s' % (jsonurl, glass_item, orgid)
        results = requests.get(glass_query, auth=(GLASSUSER, GLASSPASS))
        if 'content-length' in results.headers:
            jsonlength = int(results.headers['content-length'])
        else:
            jsonlength = len(results.text)
        if results.status_code == 200:
            if jsonlength > 22:
                txt_dir = '%s/txt' % dumpdir
                csv_dir = '%s/csv' % dumpdir
                os.makedirs(txt_dir, exist_ok=True)
                os.makedirs(csv_dir, exist_ok=True)
                dataframe = pandas.read_json(results.text)
                dataframe.to_csv()
                o_f = dataframe.loc[:, ['query', 'id']]
                o_f['sitename'] = sitename
                outcolumns = ['id', 'sitename', 'query']
                csvout = o_f.to_csv(columns=outcolumns, index=False)
                rightnow = datetime.datetime.now()
                dstamp = rightnow.strftime("%Y%m%d")
                tstamp = rightnow.strftime("%H%M%S")
                namelist = ['glass', sitename, orgid, glass_item, dstamp, tstamp, 'csv']
                filename = (".".join(namelist))
                output_file = os.path.join(csv_dir, filename)
                my_output_obj = open(output_file, 'w')
                my_output_obj.write(csvout + '\n')
                my_output_obj.close()
            else:
                print('Site: {} OrgId: {} Small_Payload: {}'.format(sitename, orgid, jsonlength))
        else:
            print("Error occured")

if __name__ == '__main__':
    main()
