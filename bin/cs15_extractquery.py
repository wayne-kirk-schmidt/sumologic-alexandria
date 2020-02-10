#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: Extracts specific Sumo Logic client queries from a CSV dump file

Usage:
   $ python  cs15_extractquery.py [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           extractquery
    @version        0.9.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 0.90
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import os
import sys
from threading import Thread
import queue
import pathlib
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

WORKERS = 32
if ARGS.workers:
    WORKERS = int(ARGS.workers)

WORKERQUEUE = queue.Queue()

RIGHTNOW = datetime.datetime.now()
DSTAMP = RIGHTNOW.strftime("%Y%m%d")
TSTAMP = RIGHTNOW.strftime("%H%M%S")

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
        extractquery(target_item)
        WORKERQUEUE.task_done()

def extractquery(glassfile):
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
        dstfile = dstname.replace(".csv", listindex)
        targetfile = os.path.join(dstdir, dstfile)
        fileobj = open(targetfile, "w")
        fileobj.write(rowvalue)
        fileobj.write('\n')
        fileobj.close()
        ### sumowash

if __name__ == '__main__':
    main()
