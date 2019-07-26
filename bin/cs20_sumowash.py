#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: cleanup existing query files

Usage:
   $ python  sumowash [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           sumowash
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
import re
import sys
import shutil
import pandas

sys.dont_write_bytecode = 1

MY_CFG = 'undefined'
PARSER = argparse.ArgumentParser(description="""

This script will cleanup syntax as much as possible for an input file.
It will collect information on the type and number of commands used.

""")

PARSER.add_argument('-f', metavar='<srcfile>', dest='srcfile', help='file to cleanup')
PARSER.add_argument('-d', metavar='<srcdir>', dest='srcdir', help='directory to cleanup')

ARGS = PARSER.parse_args()

QUERYNAME = 'SumoLogic Generated Query'
QUERYREPO = 'https://github.com/sumologic-library/generated-queries/'
QUERYAUTH = 'querylibrarian@sumologic.com'
SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
REFETCDIR = os.path.abspath(SCRIPTDIR.replace('bin', 'etc'))
TERMSFILE = os.path.join(REFETCDIR, 'operators.csv')

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
        sumowash(txtfile)

    if ARGS.srcdir:
        for txtfile in pathlib.Path(os.path.abspath(ARGS.srcdir)).rglob('*.txt'):
            sumowash(txtfile)

def setup_files(srcfile):
    """
    Creates the variables for the srcflie and dstfile
    """

    myfile = pathlib.Path(srcfile)
    dstname = myfile.with_suffix(".query")
    basedir = os.path.dirname(os.path.realpath(os.path.basename(srcfile)))

    srcfile = os.path.join(basedir, srcfile)
    dstfile = os.path.join(basedir, dstname)
    return srcfile, dstfile

def sumowash(srcfile):
    """
    This rewrites the input file to following standards
    For now this appends and regularizes white space.
    Later it will handle write space and then handle other styles
    """

    termlibrary = pandas.read_csv(TERMSFILE, header=None, index_col=0, squeeze=True).to_dict()

    (srcfile, dstfile) = setup_files(srcfile)

    srcfileobj = open(srcfile, "r")
    dstfileobj = open(dstfile, "w")
    filecontents = srcfileobj.read()
    filecontents = filecontents.replace('|', '\n|')
    filelines = filecontents.splitlines()

    dstfileobj.write('{}'.format('/*' + '\n'))
    dstfileobj.write(BEGIN.format("    Queryname:", QUERYNAME + '\n'))
    dstfileobj.write(BEGIN.format("    SourceUrl:", QUERYREPO + '\n'))
    dstfileobj.write(BEGIN.format("    Author:", QUERYAUTH + '\n'))
    dstfileobj.write('{}'.format('*/' + '\n'))

    url_list = []

    for fileline in filelines:
        fileline = fileline.rstrip()
        fileline = fileline.lstrip()
        if not fileline:
            continue
        if fileline.isspace():
            continue

        rem = re.match(r"(_\w+)\s?=\s?([\w|\S|\/]+)\s?((\S|\s+)+)?", fileline)
        if rem:
            fileline = rem.groups()[0] + '=' + '"' + '{{data_source}}' + '"'
            if rem.groups()[2]:
                fileline = fileline + ' ' + rem.groups()[2]

        com = re.match(r"(.*?)\s?[^:]\/\/\s?([\S|\s]+)?", fileline)
        if com:
            dstfileobj.write('//' + ' ' + com.groups()[1] + '\n')
            dstfileobj.write(com.groups()[0] + '\n')
        else:
            dstfileobj.write(fileline + '\n')

        for word in fileline.split():
            if word in termlibrary.keys():
                url_list.append(termlibrary[word])

    srcfileobj.close()
    url_list = list(set(url_list))

    dstfileobj.write('{}'.format('/*' + '\n'))
    for url_ref in url_list:
        dstfileobj.write(FINAL.format("    Reference:", url_ref + '\n'))
    dstfileobj.write('{}'.format('*/' + '\n'))
    dstfileobj.close()
    shutil.copyfile(dstfile, dstfile + '.txt')
    os.remove(srcfile)

if __name__ == '__main__':
    main()
