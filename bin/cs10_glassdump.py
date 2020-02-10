#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: Dumper for Sumo Logic GLASS rdscq maps supporting multiple workers

Usage:
    $ python  cs10_glassdump.py [ options ]

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
from threading import Thread
import queue
import requests
import pandas

sys.dont_write_bytecode = 1
PARSER = argparse.ArgumentParser(description="""

This will pull down the appropriate data for all specified site and orgids

""")

PARSER.add_argument('-l', metavar='<site>', dest='sitename', help='specify  glass site')
PARSER.add_argument('-i', metavar='<orgid>', dest='orgid', help='specify orgid')
PARSER.add_argument('-c', metavar='<config>', dest='config', help='specify  config')
PARSER.add_argument('-u', metavar='<user>', dest='username', help='specify  username')
PARSER.add_argument('-p', metavar='<pass>', dest='password', help='specify  password')
PARSER.add_argument('-d', metavar='<dir>', dest='destdir', help='specify output dir')
PARSER.add_argument('-w', metavar='<workers>', dest='workers', help='specify workers')

ARGS = PARSER.parse_args()

if ARGS.username:
    os.environ["GLASSUSER"] = ARGS.username
if ARGS.password:
    os.environ["GLASSPASS"] = ARGS.password

WORKERS = 32
if ARGS.workers:
    WORKERS = int(ARGS.workers)

DESTDIR = "/tmp"

if ARGS.destdir:
    DESTDIR = os.path.abspath((ARGS.destdir))

try:
    GLASSPASS = os.environ['GLASSPASS']
    GLASSUSER = os.environ['GLASSUSER']
except KeyError as myerror:
    print('Environment Variable Not Set :: {} '.format(myerror.args[0]))

GLASS_DICT = {'rdscq' : 'query'}
GLASS_LIST = list(GLASS_DICT.keys())
GLASS_ORGS = []
WORKERQUEUE = queue.Queue()

RIGHTNOW = datetime.datetime.now()
DSTAMP = RIGHTNOW.strftime("%Y%m%d")
TSTAMP = RIGHTNOW.strftime("%H%M%S")

def main():
    """
    The script will collect a list of the glass files for a given client
    After doing so, it will write this to a local directory
    """
    sitename = ARGS.sitename
    orgid = ARGS.orgid
    config = ARGS.config

    if not config:
        baseurl = 'https://%s-monitor.sumologic.net/glass' % sitename
        jsonurl = '%s/api/json/datastore/searchable/exportjson' % baseurl
        glassprep(jsonurl, sitename, orgid)
    else:
        with open(config) as cfgobj:
            for cfgline in cfgobj:
                orgid = cfgline.split(',')[0]
                sitename = cfgline.split(',')[1]
                baseurl = 'https://%s-monitor.sumologic.net/glass' % sitename
                jsonurl = '%s/api/json/datastore/searchable/exportjson' % baseurl
                glassprep(jsonurl, sitename, orgid)

    for _i in range(WORKERS):
        glassthread = Thread(target=glassworker)
        glassthread.daemon = True
        glassthread.start()

    WORKERQUEUE.join()

def glassprep(jsonurl, sitename, orgid):
    """
    This packs a data structure we will put onto a queue for processing
    The design is enqueue serially, and dequeue in parallel
    """

    for glass_item in GLASS_LIST:
        glass_query = '%s/%s?orgid=%s' % (jsonurl, glass_item, orgid)
        glass_items = '%s#%s#%s#%s' % (sitename, orgid, glass_item, glass_query)
        WORKERQUEUE.put(glass_items)

def glassworker():
    """
    A wrapper for the collectdata subroutine. Each of the workers defined will run this code
    """
    while True:
        target_item = WORKERQUEUE.get()
        collectdata(target_item)
        WORKERQUEUE.task_done()

def createdirs(sitename, orgid):
    """
    This will create the directories required for the glass dump.
    each directory will have files in each subdirectory of the dump directory.

    csv - raw glass output
    txt - extracted files from the csv files
    slq - normalized data
    """

    dumpdir = '%s/cscontent/output/%s/%s' % (DESTDIR, sitename, orgid)
    os.makedirs(dumpdir, exist_ok=True)

    txt_dir = '%s/txt' % dumpdir
    os.makedirs(txt_dir, exist_ok=True)

    csv_dir = '%s/csv' % dumpdir
    os.makedirs(csv_dir, exist_ok=True)

    slq_dir = '%s/slq' % dumpdir
    os.makedirs(slq_dir, exist_ok=True)

    return csv_dir

def collectdata(target_item):
    """
    This collects the data and writes out to the output file.
    It will call createdirs as a byproduct of the collectioin.
    """

    (sitename, orgid, glass_item, glass_query) = target_item.split('#')

    filelist = ['glass', sitename, orgid, glass_item, 'csv']
    output_file = os.path.join(createdirs(sitename, orgid), (".".join(filelist)))

    filelist = ['glass', sitename, orgid, glass_item, DSTAMP, TSTAMP, 'err']
    errors_file = os.path.join(createdirs(sitename, orgid), (".".join(filelist)))

    results = requests.get(glass_query, auth=(GLASSUSER, GLASSPASS))
    if 'content-length' in results.headers:
        jsonlength = int(results.headers['content-length'])
    else:
        jsonlength = len(results.text)
    if results.status_code == 200:
        if jsonlength > 22:
            dataframe = pandas.read_json(results.text)
            dataframe.to_csv()
            o_f = dataframe.loc[:, ['query', 'id']]
            o_f['sitename'] = sitename
            outcolumns = ['id', 'sitename', 'query']
            csvout = o_f.to_csv(columns=outcolumns, index=False)
            my_output_obj = open(output_file, 'w')
            my_output_obj.write(csvout + '\n')
            my_output_obj.close()
        else:
            csvout = 'site: %s orgid: %s SmallPayload: %s'  % (sitename, orgid, jsonlength)
            my_output_obj = open(errors_file, 'w')
            my_output_obj.write(csvout + '\n')
            my_output_obj.close()
    else:
        csvout = 'site: %s orgid: %s ErrorOccured: %s'  % (sitename, orgid, results.status_code)
        my_output_obj = open(errors_file, 'w')
        my_output_obj.write(csvout + '\n')
        my_output_obj.close()

if __name__ == '__main__':
    main()
