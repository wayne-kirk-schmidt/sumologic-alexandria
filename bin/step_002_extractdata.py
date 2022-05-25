#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: Dumper for Sumo Logic GLASS rdscq maps supporting multiple workers

Usage:
    $ python  step_002_extractdata [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           step_002_extractdata
    @version        1.0.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   APACHE 2.0
    @license-url    http://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = 1.0
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import datetime
import os
import sys
from threading import Thread
from collections import defaultdict
import queue
import requests
import pandas

sys.dont_write_bytecode = 1
PARSER = argparse.ArgumentParser(description="""

This will pull down the raw rdscq data

""")

PARSER.add_argument('-s', metavar='<site>', default='all', \
                    dest='sitename', help='specify  glass site')

PARSER.add_argument('-c', metavar='<config>', dest='config', help='specify  config')

PARSER.add_argument('-u', metavar='<user>', dest='username', help='specify  username')

PARSER.add_argument('-p', metavar='<pass>', dest='password', help='specify  password')

PARSER.add_argument('-d', metavar='<dumpdir>', default='/var/tmp/glassdump', \
                    dest='dumpdir', help='specify dumpdir')

PARSER.add_argument('-w', metavar='<workers>', default=1, \
                    dest='workers', help='specify workers')

ARGS = PARSER.parse_args()

SITENAME = ARGS.sitename

GLASSUSER = ARGS.username

GLASSPASS = ARGS.password

DEPLOYMENTDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../etc'))

DEPLOYMENTLIST = os.path.join(DEPLOYMENTDIR, 'sitelist.cfg')

RIGHTNOW = datetime.datetime.now()

DSTAMP = RIGHTNOW.strftime("%Y%m%d")
TSTAMP = RIGHTNOW.strftime("%H%M%S")

WORKERS = int(ARGS.workers)

DUMPDIR = os.path.abspath((ARGS.dumpdir))

WORKERQUEUE = queue.Queue()

RIGHTNOW = datetime.datetime.now()

DSTAMP = RIGHTNOW.strftime("%Y%m%d")

TSTAMP = RIGHTNOW.strftime("%H%M%S")

ERRORS = defaultdict(int)

def main():
    """
    This will look for a list of clients within a glass client config file
    Using this file, it will create all of the queries it needs and use
    A pool of workers to drain the queue.
    """

    deploymentlist = []

    if SITENAME == 'all':
        with open(DEPLOYMENTLIST, "r", encoding='utf8') as listobject:
            deploymentlist = listobject.readlines()
    else:
        deploymentlist.append(SITENAME)

    for deployment in deploymentlist:
        configfile = f'{DUMPDIR}/cfg/{deployment}/{deployment}.csv'
        with open(configfile, 'r', encoding='utf8') as cfgobj:
            for cfgline in cfgobj:
                orgid = cfgline.split(',')[0]
                sitename = cfgline.split(',')[1]
                baseurl = f'https://{sitename}-monitor.sumologic.net/glass'
                jsonurl = f'{baseurl}/api/json/datastore/searchable/exportjson'
                glassprep(jsonurl, sitename, orgid)
                ### print(f'PREPARING: {sitename},{orgid},{jsonurl}')

    for _i in range(WORKERS):
        glassthread = Thread(target=glassworker)
        glassthread.daemon = True
        glassthread.start()

    WORKERQUEUE.join()
  
    for error_key, error_value in ERRORS.items():
        print(f'ISSUES - {error_key} - {error_value}')

def glassprep(jsonurl, sitename, orgid):
    """
    This packs a data structure we will put onto a queue for processing
    The design is enqueue serially, and dequeue in parallel
    """

    glass_item = 'rdscq'
    glass_query = f'{jsonurl}/{glass_item}?orgid={orgid}'
    glass_items = f'{sitename}#{orgid}#{glass_item}#{glass_query}'
    WORKERQUEUE.put(glass_items)

def glassworker():
    """
    A wrapper for the collectdata subroutine. Each of the workers defined will run this code
    """
    while True:
        target_item = WORKERQUEUE.get()
        collectdata(target_item)
        WORKERQUEUE.task_done()

def collectdata(target_item):
    """
    This collects the data and writes out to the output file.
    """

    (sitename, orgid, glass_item, glass_query) = target_item.split('#')

    print(f'PROCESSING: {orgid}')

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

            dumpdir = f'{DUMPDIR}/output/{sitename}/{orgid}'
            os.makedirs(dumpdir, exist_ok=True)

            csv_dir = f'{DUMPDIR}/output/{sitename}/{orgid}/csv'
            os.makedirs(csv_dir, exist_ok=True)

            csv_file = f'{csv_dir}/glass.{sitename}.{orgid}.{glass_item}.csv'

            with open(csv_file, 'w', encoding='utf8') as my_output_obj:
                my_output_obj.write(csvout + '\n')
        else:
            ERRORS['short-payload'] += 1
    else:
        ERRORS[f'error-{results.status_code}'] += 1

if __name__ == '__main__':
    main()
