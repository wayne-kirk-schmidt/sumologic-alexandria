SumoLogic Library
=================

SumoLogic is a suite of tools to query, extract, organize, and query against SumoLogic content.
The goal of the scripts are to build a library of content, and organize them into "families" of functionality.

Installing the Scripts
=======================

The scripts are command line based, designed to be used within a batch script or DevOPs tool such as Cher or Ansible.
Each script is a python3 script, and the complete list of the python modules will be provided to aid people using a pip install.

You will need to use Python 3.6 or higher and the modules listed in the dependency section.  

The steps are as follows: 

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

    1. cs05_getclients.py - collect a list of organizational id or ids.

    2. cs10_glassdump.py - using the collector id or ids, download the rdsqs for that orgid.

    3. cs15_querydump.py - extract out each query from the downloaded master file

    4. cs20_sumowash.py - normalize the query syntax, and document the query

NOTE: in the future this will also include a critique of the syntax, and offer suggestions for improvement

    5. cs25_querydata.py - query the information for a query or queries for a given orgid or orgids.

NOTE: this can store the information into a pickle file for later use.

    6. cs30_unpickle.py - this provides a summary of queries information and will be combined into a single script.

    7. cs35_gherkin.py - this provides a fingerprint of queries and will be combined into a single script.
        
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

