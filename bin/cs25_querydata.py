#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: collect useful information from the files that have been cleaned up.

Usage:
   $ python  querydata [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           querydata
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
import pathlib
import pickle
import json
import re
import sys
import pandas

sys.dont_write_bytecode = 1

MY_CFG = 'undefined'
PARSER = argparse.ArgumentParser(description="""

This script will cleanup syntax as much as possible for an input file.
It will collect information on the type and number of commands used.

""")

PARSER.add_argument('-f', metavar='<srcfile>', dest='srcfile', help='file to cleanup')
PARSER.add_argument('-d', metavar='<srcdir>', dest='srcdir', help='directory to cleanup')
PARSER.add_argument('-p', metavar='<picklefile>', dest='picklefile', help='store our data')

ARGS = PARSER.parse_args()

SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
REFETCDIR = os.path.abspath(SCRIPTDIR.replace('bin', 'etc'))
TERMSFILE = os.path.join(REFETCDIR, 'operators.csv')

SUMOWISDOM = dict()
PICKLEFILE = ARGS.picklefile

def main():
    """
    The the main part of querydata. This collects data and stores into a CSV
    This will be changed to other data types.
    """

    if ARGS.srcfile:
        txtfile = os.path.abspath(ARGS.srcfile)
        querydata(txtfile)

    if ARGS.srcdir:
        for txtfile in pathlib.Path(os.path.abspath(ARGS.srcdir)).rglob('*.query'):
            querydata(txtfile)

    if PICKLEFILE:
        pickle.dump(SUMOWISDOM, open(PICKLEFILE, "wb"))
    else:
        print(json.dumps(SUMOWISDOM, indent=4, sort_keys=True))


def build_wisdom(srcfile, querylines):
    """
    Structure the ouptut of the data found in the query
    this data is saved into a pickle file for later use
    """

    termlibrary = pandas.read_csv(TERMSFILE, header=None, index_col=0, squeeze=True).to_dict()

    sllist = (os.path.basename(srcfile).split('.'))
    sls = sllist[1]
    slo = sllist[2]
    slt = sllist[3]
    sli = int(sllist[6])

    if not sls in SUMOWISDOM.keys():
        SUMOWISDOM[sls] = dict()
    if not slo in SUMOWISDOM[sls].keys():
        SUMOWISDOM[sls][slo] = dict()
    if not slt in SUMOWISDOM[sls][slo].keys():
        SUMOWISDOM[sls][slo][slt] = dict()
    SUMOWISDOM[sls][slo][slt][sli] = list()

    for queryline in querylines:
        queryline = (re.sub('[=()"]', ' ', queryline))
        for word in queryline.split():
            if word in termlibrary.keys() or word.startswith('_'):
                SUMOWISDOM[sls][slo][slt][sli].append(word)
    return SUMOWISDOM

def querydata(srcfile):
    """
    Currently this will look for keywords and show them in order
    Additionally, it will calculate the frequency of keyword use
    """

    srcfileobj = open(srcfile, "r")
    filelines = srcfileobj.readlines()

    with_delimiting_lines = True
    start_regex = re.compile(r'/\*')
    final_regex = re.compile(r'\*/')
    querylines = []
    group_list = []

    inside_group = False
    for linenl in filelines:
        line = linenl.rstrip()
        if inside_group:
            if start_regex.match(line):
                inside_group = False
                if with_delimiting_lines:
                    group.append(line)
                group_list.append(group)
            else:
                querylines.append(line)
        elif final_regex.match(line):
            inside_group = True
            group = []
            if with_delimiting_lines:
                group.append(line)
    srcfileobj.close()

    build_wisdom(srcfile, querylines)

if __name__ == '__main__':
    main()
