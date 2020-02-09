#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: Extracts specific Sumo Logic client queries from a CSV dump file

Usage:
   $ python  cs15_querydump.py [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           querydump
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
import pathlib
import pandas

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This will extract Sumo Logic queries from a single dump file

""")

PARSER.add_argument('-f', metavar='<srcfile>', dest='srcfile', help='input file to cleanup')
PARSER.add_argument('-d', metavar='<srcdir>', dest='srcdir', help='input directory to cleanup')
PARSER.add_argument('-q', metavar='<query>', dest='query', default='query', help='tag to use')

ARGS = PARSER.parse_args()

def main():
    """
    This is a driver for extract the CSV files and any other transform required
    """
    if ARGS.srcfile:
        csvfile = ARGS.srcfile
        querydump(csvfile)
    if ARGS.srcdir:
        for csvfile in pathlib.Path(ARGS.srcdir).rglob('*.csv'):
            querydump(csvfile)

def querydump(glassfile):
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

if __name__ == '__main__':
    main()
