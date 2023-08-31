#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: Assemble information on Sumo Logic sanitized client queries

Usage:
   $ python step_004_querydata.py [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           querydata
    @version        0.4.00
    @author-name    Wayne Schmidt
    @author-email   wayne.kirk.schmidt@gmail.com
    @license-name   APACHE 2.0
    @license-url    http://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = 0.40
__author__ = "Wayne Kirk Schmidt (wayne.kirk.schmidt@gmail.com)"

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
PARSER.add_argument('-d', metavar='<srcdir>', dest='srcdir', help='specify target directory')
PARSER.add_argument('-p', metavar='<picklefile>', dest='picklefile', help='specify data storage')

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
        for txtfile in pathlib.Path(os.path.abspath(ARGS.srcdir)).rglob('*.slq'):
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

    ### sls - Sumo Logic Site
    sls = sllist[0]

    ### slo - Sumo Logic Organization
    slo = sllist[1]

    ### slo - Sumo Logic Query Type
    slt = sllist[2]

    ### slo - Sumo Logic Query Index
    sli = int(sllist[4])

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

    with open(srcfile, "r") as srcfileobj:
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

        build_wisdom(srcfile, querylines)

if __name__ == '__main__':
    main()
