#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: dumps out query files from a central csv file

Usage:
   $ python  querydump [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           querydump
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
import sys
import pathlib
import pandas

sys.dont_write_bytecode = 1

PARSER = argparse.ArgumentParser(description="""

This script will cleanup syntax as much as possible for an input file.
It will collect information on the type and number of commands used.

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
    topdir = os.path.dirname(srcdir)
    dstdir = os.path.join(topdir, 'txt')
    srcfile = glassfile
    myfile = str(os.path.splitext(os.path.basename(glassfile))[0])

    if not os.path.exists(dstdir):
        print(dstdir)
        os.mkdir(dstdir)

    csv_data = pandas.read_csv(srcfile)

    datalist = csv_data.loc[:, ARGS.query]
    for index, rowvalue in datalist.iteritems():
        targetfile = myfile + "." + str(index) + ".txt"
        dstfile = os.path.join(dstdir, targetfile)
        fileobj = open(dstfile, "w")
        fileobj.write(rowvalue)
        fileobj.write('\n')
        fileobj.close()

if __name__ == '__main__':
    main()
