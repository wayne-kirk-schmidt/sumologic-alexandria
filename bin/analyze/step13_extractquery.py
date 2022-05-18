#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: Extracts specific Sumo Logic client queries from a CSV dump file

Usage:
   $ python  cs13_extractquery.py [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           extractquery
    @version        0.9.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   APACHE 2.0
    @license-url    http://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = 0.90
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import os
import sys
from threading import Thread
import queue
import pathlib
import re
import datetime
import pandas

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This will extract Sumo Logic queries from a single dump file

""")

PARSER.add_argument('-f', metavar='<srcfile>', dest='srcfile', help='specify file to cleanup')
PARSER.add_argument('-d', metavar='<srcdir>', dest='srcdir', help='specify directory to cleanup')
PARSER.add_argument('-q', metavar='<query>', dest='query', default='query', help='specify tag')
PARSER.add_argument('-w', metavar='<workers>', dest='workers', help='specify workers')

ARGS = PARSER.parse_args()

RIGHTNOW = datetime.datetime.now()
DSTAMP = RIGHTNOW.strftime("%Y%m%d")
TSTAMP = RIGHTNOW.strftime("%H%M%S")

QUERYNAME = 'Sumo Logic Generated Query'
QUERYREPO = 'https://github.com/sumologic-library/generated-queries/'
QUERYAUTH = 'querylibrarian@sumologic.com'
SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
REFETCDIR = os.path.abspath(SCRIPTDIR.replace('bin', 'etc'))
TERMSFILE = os.path.join(REFETCDIR, 'operators.csv')
TERMSDICT = pandas.read_csv(TERMSFILE, header=None, index_col=0, squeeze=True).to_dict()

WORKERS = 32
if ARGS.workers:
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
    if ARGS.srcfile:
        csvfile = ARGS.srcfile
        WORKERQUEUE.put(csvfile)

    if ARGS.srcdir:
        for csvfile in pathlib.Path(ARGS.srcdir).rglob('*.csv'):
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

    srcdir = os.path.abspath(os.path.dirname(os.path.realpath(glassfile)))
    srcfile = os.path.realpath(glassfile)

    dstdir = srcdir.replace("/csv", "/txt")
    dstname = os.path.basename(os.path.realpath(glassfile))

    if not os.path.exists(dstdir):
        os.mkdir(dstdir)

    csv_data = pandas.read_csv(srcfile)

    datalist = csv_data.loc[:, ARGS.query]
    for index, rowvalue in datalist.iteritems():
        listindex = "." + str(index) + ".txt"
        targetfile = dstname.replace(".csv", listindex)
        dstfile = os.path.join(dstdir, targetfile)
        with open(dstfile, "w") as fileobj:
            fileobj.write(rowvalue)
            fileobj.write('\n')
        target_item = slqprep(dstfile)
        sumowash(target_item)

def slqprep(txtfile):
    """
    This prepares the srcdir, srcfile and dstdir, and dstfile
    it returns the files to be used to read and create the sanitized queries
    """

    srcdir = os.path.abspath(os.path.dirname(os.path.realpath(txtfile)))
    srcfile = os.path.realpath(txtfile)

    dstdir = srcdir.replace("/txt", "/slq")
    dstname = (os.path.basename(os.path.realpath(txtfile))).replace(".txt", ".slq")
    dstfile = os.path.realpath(os.path.join(dstdir, dstname))

    if not os.path.exists(dstdir):
        os.mkdir(dstdir)

    glass_item = '%s#%s' % (srcfile, dstfile)
    return glass_item

def sumowash(target_item):
    """
    This rewrites the input file to following standards
    For now this appends and regularizes white space.
    """

    (srcfile, dstfile) = target_item.split('#')

    with open(srcfile, "r") as srcfileobj:
        filecontents = srcfileobj.read()

    with open(dstfile, "w") as dstfileobj:
        dstfileobj.write('{}'.format('/*' + '\n'))
        dstfileobj.write(BEGIN.format("    Queryname:", QUERYNAME + '\n'))
        dstfileobj.write(BEGIN.format("    SourceUrl:", QUERYREPO + '\n'))
        dstfileobj.write(BEGIN.format("    Author:", QUERYAUTH + '\n'))
        dstfileobj.write('{}'.format('*/' + '\n'))

    url_list = []

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
            if rem.groups()[2]:
                fileline = fileline + ' ' + rem.groups()[2]

        rem = re.match(r"(.*?)([^:]\/{2}.*?)?$", fileline)
        if rem.groups()[1]:
            fileline = rem.groups()[0]+ '\n' + rem.groups()[1].lstrip()

        fileline = re.sub(r'(\s|\w)\|(\s|\w)', r'\n|\1', fileline)
        fileline = fileline.lstrip()

        dstfileobj.write(fileline + '\n')
        for word in fileline.split():
            if word in TERMSDICT.keys():
                url_list.append(TERMSDICT[word])

    srcfileobj.close()
    url_list = list(set(url_list))

    dstfileobj.write('{}'.format('/*' + '\n'))
    for url_ref in url_list:
        dstfileobj.write(FINAL.format("    Reference:", url_ref + '\n'))
    dstfileobj.write('{}'.format('*/' + '\n'))
    dstfileobj.close()

if __name__ == '__main__':
    main()
