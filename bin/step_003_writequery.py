#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=E1101
# pylint: disable=C0209

"""
Explanation: Extracts specific Sumo Logic client queries from the CSV dump file

Usage:
   $ python  step_003_writequery [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           step_003_writequery
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
import csv
import sys
from threading import Thread
import queue
import pathlib
import re
import datetime
import pandas

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This extracts Sumo Logic queries from a single dump file

""")

PARSER.add_argument('-s', metavar='<site>', default='all', \
                    dest='sitename', help='specify  glass site')

PARSER.add_argument('-d', metavar='<dumpdir>', default='/var/tmp/glassdump', \
                    dest='dumpdir', help='specify dumpdir')

PARSER.add_argument('-w', metavar='<workers>', default=8, \
                    dest='workers', help='specify workers')

ARGS = PARSER.parse_args()

SITENAME = ARGS.sitename

DUMPDIR = ARGS.dumpdir

DEPLOYMENTDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../etc'))

DEPLOYMENTLIST = os.path.join(DEPLOYMENTDIR, 'sitelist.cfg')

CLASSIFIERCFG = os.path.join(DEPLOYMENTDIR, 'classifier.csv')

CLASSIFIERDICT = {}

with open(CLASSIFIERCFG, 'r', encoding='utf8') as FILEOBJECT:
    READEROBJECT = csv.reader(FILEOBJECT, delimiter=',')
    for csvrow in READEROBJECT:
        csvkey, csvvalue = csvrow
        CLASSIFIERDICT[csvkey] = csvvalue

RIGHTNOW = datetime.datetime.now()

DSTAMP = RIGHTNOW.strftime("%Y%m%d")
TSTAMP = RIGHTNOW.strftime("%H%M%S")

QUERYNAME = 'Sumo Logic Generated Query'

QUERYREPO = 'https://github.com/sumologic-library/generated-queries/'

QUERYAUTH = 'querylibrarian@sumologic.com'

SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
REFETCDIR = os.path.abspath(os.path.join(SCRIPTDIR, '../etc'))

TERMSFILE = os.path.join(REFETCDIR, 'operators.csv')

TERMSDICT = pandas.read_csv(TERMSFILE, header=None, index_col=0).squeeze("columns").to_dict()

WORKERS = int(ARGS.workers)

WORKERQUEUE = queue.Queue()

RIGHTNOW = datetime.datetime.now()

DSTAMP = RIGHTNOW.strftime("%Y%m%d")
TSTAMP = RIGHTNOW.strftime("%H%M%S")

BEGIN = "{0:<20}{1:}"
QUERY = "{0:}"
FINAL = "{0:<20}{1:}"

def main():
    """
    This is a driver for extract the CSV files and any other transform required
    """

    deploymentlist = []

    if SITENAME == 'all':
        with open(DEPLOYMENTLIST, "r", encoding='utf8') as listobject:
            deploymentlist = listobject.readlines()
    else:
        deploymentlist.append(SITENAME)

    for deployment in deploymentlist:
        deployment = deployment.rstrip()
        for csvfile in pathlib.Path(DUMPDIR).rglob('*rdscq.csv'):
            WORKERQUEUE.put(csvfile)

    for _i in range(WORKERS):
        glassthread = Thread(target=glassworker)
        glassthread.daemon = True
        glassthread.start()

    WORKERQUEUE.join()

def glassworker():
    """
    A wrapper for the collectdata subroutine. Each of the workers defined will run this code
    """
    while True:
        target_item = WORKERQUEUE.get()
        extractwash(target_item)
        WORKERQUEUE.task_done()

def extractwash(glassfile):
    """
    This will take the specific file, then run the extraction method.
    Using pandas, this extracts the relevant query out of the CSV file.
    """

    srcdir = os.path.realpath(os.path.dirname(os.path.realpath(glassfile)))

    txtdir = os.path.realpath(os.path.join(srcdir, '../txt'))
    os.makedirs(txtdir, exist_ok=True)

    slqdir = os.path.realpath(os.path.join(srcdir, '../slq'))
    os.makedirs(slqdir, exist_ok=True)

    srcfile = os.path.realpath(glassfile)

    csvbase = os.path.join(txtdir, os.path.basename(glassfile)).removesuffix('.csv')

    slqbase = os.path.join(slqdir, os.path.basename(glassfile)).removesuffix('.csv')

    csv_data = pandas.read_csv(srcfile)

    datalist = csv_data.loc[:, 'query']
    for index, rowvalue in datalist.iteritems():

        txtfile = f'{csvbase}.{str(index)}.txt'
        slqfile = f'{slqbase}.{str(index)}.txt'
        profile = f'{slqbase}.{str(index)}.profile.txt'

        with open(txtfile, "w", encoding='utf8') as fileobj:
            fileobj.write(rowvalue)
            fileobj.write('\n')
        sumowash(txtfile,slqfile,profile)

def sumowash(mysrcfile,mydstfile,myprofilefile):
    """
    This rewrites the input file to following standards
    For now this appends and regularizes white space.
    """

    with open(mysrcfile, "r", encoding='utf8') as srcobj:
        filecontents = srcobj.read()

    with open(mydstfile, "a+", encoding='utf8') as dstfileobj:
        dstfileobj.write('{}'.format('/*' + '\n'))
        dstfileobj.write(BEGIN.format("    Queryname:", QUERYNAME + '\n'))
        dstfileobj.write(BEGIN.format("    SourceUrl:", QUERYREPO + '\n'))
        dstfileobj.write(BEGIN.format("    Author:", QUERYAUTH + '\n'))
        dstfileobj.write('{}'.format('*/' + '\n'))

        url_list = []
        keyword_list = []

        for fileline in filecontents.splitlines():
            fileline = fileline.rstrip()
            fileline = fileline.lstrip()
            if not fileline:
                continue
            if fileline.isspace():
                continue

            ### java comments ### .*?([^:]\/{2}.*?$)
            ### c++ comments  ### /\*(\s|\S)+\*/

            rem = re.match(r"(_\w+)\s?=\s?([\w|\S|\/]+)\s?((\S|\s+)+)?", fileline)
            if rem:
                fileline = rem.groups()[0] + '=' + '"' + '{{data_source}}' + '"'
                if rem.groups()[0] in CLASSIFIERDICT:
                    keyword_list.append(CLASSIFIERDICT[rem.groups()[0]])
                if rem.groups()[2]:
                    fileline = fileline + ' ' + rem.groups()[2]

            rem = re.match(r"(.*?)([^:]\/{2}.*?)?$", fileline)
            if rem.groups()[1]:
                fileline = rem.groups()[0]+ '\n' + rem.groups()[1].lstrip()

            fileline = re.sub(r'(\s|\w)\|(\s|\w)', r'\n|\1', fileline)
            fileline = fileline.lstrip()

            dstfileobj.write(fileline + '\n')
            fileline = re.sub(r'\W+\s*', ' ', fileline)
            for word in fileline.split():
                if word in TERMSDICT.keys():
                    url_list.append(TERMSDICT[word])
                if word in CLASSIFIERDICT:
                    keyword_list.append(CLASSIFIERDICT[word])

        url_list = list(set(url_list))

        dstfileobj.write('{}'.format('/*' + '\n'))
        for url_ref in url_list:
            dstfileobj.write(FINAL.format("    Reference:", url_ref + '\n'))
        dstfileobj.write('{}'.format('*/' + '\n'))

        with open(myprofilefile, "w", encoding='utf8') as profileobject:
            keyword_string = "-".join(keyword_list)
            profileobject.write(f'{mydstfile},{keyword_string}\n')

    os.remove(mysrcfile)

if __name__ == '__main__':
    main()
