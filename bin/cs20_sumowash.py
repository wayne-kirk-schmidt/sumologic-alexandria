#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: Perform initial cleanup of Sumo Logic client query syntax

Usage:
   $ python  cs20_sumowash.py [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           sumowash
    @version        0.9.0
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 0.90
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import datetime
import os
import pathlib
import re
import sys
from threading import Thread
import queue
import pandas

sys.dont_write_bytecode = 1

MY_CFG = 'undefined'
PARSER = argparse.ArgumentParser(description="""

This script will cleanup syntax as much as possible for an input file.

""")

PARSER.add_argument('-f', metavar='<srcfile>', dest='srcfile', help='file to cleanup')
PARSER.add_argument('-d', metavar='<srcdir>', dest='srcdir', help='directory to cleanup')
PARSER.add_argument('-w', metavar='<workers>', dest='workers', help='specify workers')

ARGS = PARSER.parse_args()

QUERYNAME = 'SumoLogic Generated Query'
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
    The the main part of sumowash. This will be extended to keyword linking
    and other functions, for now, this is a rewriter
    """

    if ARGS.srcfile:
        txtfile = os.path.abspath(ARGS.srcfile)
        sumoprep(txtfile)

    if ARGS.srcdir:
        for txtfile in pathlib.Path(os.path.abspath(ARGS.srcdir)).rglob('*.txt'):
            sumoprep(txtfile)

    for _i in range(WORKERS):
        glassthread = Thread(target=glassworker)
        glassthread.daemon = True
        glassthread.start()

    WORKERQUEUE.join()

def sumoprep(txtfile):
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
    WORKERQUEUE.put(glass_item)

def glassworker():
    """
    A wrapper for the collectdata subroutine. Each of the workers defined will run this code
    """
    while True:
        target_item = WORKERQUEUE.get()
        sumowash(target_item)
        WORKERQUEUE.task_done()

def sumowash(target_item):
    """
    This rewrites the input file to following standards
    For now this appends and regularizes white space.
    """

    (srcfile, dstfile) = target_item.split('#')

    srcfileobj = open(srcfile, "r")
    dstfileobj = open(dstfile, "w")
    filecontents = srcfileobj.read()

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
