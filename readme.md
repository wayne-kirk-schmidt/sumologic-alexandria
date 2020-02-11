
Alexandria - The Sumo Logic Query Library
=========================================

Alexandria is a suite of tools to query, extract, organize, and query against Sumo Logic content.
The goal of the scripts are to build a library of content, and organize  them into "families" of functionality.

Installing the Scripts
=======================

The scripts are command line based, designed to be used within a batch script or DevOPs tool such as Chef or Ansible.
Written in python3, all scripts are listed below, and there is a Pipfile to show what modules are required to run.

You will need to use Python 3.6 or higher and the modules listed in the dependency section.  

Please follow the following steps to install:

    1. Download and install python 3.6 or higher from python.org. Append python3 to the LIB and PATH env.

    2. Download and install git for your platform if you don't already have it installed.
       It can be downloaded from https://git-scm.com/downloads
    
    3. Open a new shell/command prompt. It must be new since only a new shell will include the new python 
       path that was created in step 1. Cd to the folder where you want to install the scripts.
    
    4. Execute the following command to install pipenv, which will manage all of the library dependencies:
    
        sudo -H pip3 install pipenv 
 
    5. Clone this repo using the following command:
    
        git clone git@github.com:wks-sumo-logic/sumologic-toshokan.git

    This will create a new folder sumologic-toshokan
    
    6. Change into the sumologic-toshokan folder. Type the following to install all the package dependencies 
       (this may take a while as this will download all of the libraries that sumotoolbox uses):

        pipenv install
        
Dependencies
============

See the contents of "pipfile"

Script Names and Purposes
=========================

Scripts and Functions:

    1. cs11_getclients.py - get a list of organizational ids from a given deployment site

    2. cs12_glassdump.py - dump all consolidated queries for a given organizational id and site

    3. cs13_extractquery.py - split queries into specific files and perform basic hygiene

NOTE: in the future we will have scripts/modules to critique syntax, and offer improvement suggestions

    4. cs21_querydata.py - query the information for a query or queries for a given orgid or orgids.

NOTE: this can store the information into a pickle file for later use.

    5. cs22_unpickle.py	- this provides a summary of query information

    6. cs23_gherkin.py - this provides a fingerprint of all queries
        
To Do List:
===========

* Extend the pickle file information for the content

* Build an Ansible wrapper for the scripts

* Add depdndency checking for pip modules

* Fix remaining pylint issues/points

* add wrapper for exporting queries into a HTML tree and other components

License
=======

Copyright 2019 Wayne Kirk Schmidt

Licensed under the GNU GPL License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    license-name   GNU GPL
    license-url    http://www.gnu.org/licenses/gpl.html

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Support
=======

Feel free to e-mail me with issues to: wschmidt@sumologic.com
I will provide "best effort" fixes and extend the scripts.
/Users/wschmidt/Downloads/sumologictoolbox-master/Pipfile

Famous Libraries
================

[Famous Libraries of the World](http://www.mastersinlibraryscience.net/25-most-famous-libraries-of-the-world/)

