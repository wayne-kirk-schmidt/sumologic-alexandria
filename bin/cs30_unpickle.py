#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation: load up pickled python data for basic analysis

Usage:
   $ python  unpickle [ options ]

Style:
   Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

    @name           unpickle
    @version        0.4.00
    @author-name    Wayne Schmidt
    @author-email   wschmidt@sumologic.com
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html
"""

__version__ = 0.40
__author__ = "Wayne Schmidt (wschmidt@sumologic.com)"

import argparse
import pickle
import os
import sys

sys.dont_write_bytecode = 1

MY_CFG = 'undefined'
PARSER = argparse.ArgumentParser(description="""

This script will perform basic sumo wisdom calculations
currently in line, this would be extended into libraries
Long term goal is have this loaded into sumo itself

""")

PARSER.add_argument('-p', metavar='<picklefile>', dest='picklefile', help='store our data')

ARGS = PARSER.parse_args()

PICKLEFILE = ARGS.picklefile

def main():
    """
    This is the main part of the script. This will load the file and read in
    the structure. It will perform basic calculations
    """

    if PICKLEFILE:
        unpickle(os.path.abspath(PICKLEFILE))
    else:
        sys.exit()

def unpickle(srcfile):
    """
    Currently this will look for keywords and show them in order
    Additionally, it will calculate the frequency of keyword use
    """

    wtotal = 0
    ototal = 0
    qtotal = 0

    srcfileobj = open(srcfile, 'rb')
    sumowisdom = pickle.load(srcfileobj)
    for key1 in sumowisdom.keys():
        for key2 in sumowisdom[key1].keys():
            ototal = ototal + 1
            for key3 in sumowisdom[key1][key2].keys():
                for key4 in sumowisdom[key1][key2][key3].keys():
                    qtotal = qtotal + 1
                    wordcount = len(sumowisdom[key1][key2][key3][key4])
                    ### print('{} {} {} {} {}'.format(key1, key2, key3, key4, wordcount))
                    wtotal = wtotal + wordcount
    srcfileobj.close()

    print('Total Orgs:\t\t{:10}'.format(ototal))
    print('Total Queries:\t\t{:10}'.format(qtotal))
    print('Total Words:\t\t{:10}'.format(wtotal))
    print('Average Words:\t\t{:10}'.format(int(wtotal/qtotal)))

if __name__ == '__main__':
    main()
