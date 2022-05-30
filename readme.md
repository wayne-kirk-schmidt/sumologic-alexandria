
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
 
    5. Clone this repository. This will create a new folder

    6. Change into the new folder. Type the following to install all the package dependencies 
       (this may take a while as this will download all of the libraries required):

        pipenv install
        
Dependencies
============

See the contents of "pipfile"

Script Names and Purposes
=========================

Scripts and Functions:

```
bin
└── build
    ├── step_001_listclients.py
    ├── step_002_extractdata.py
    └── step_003_writequery.py
```
* Listclients gets a list of clients from each deployment, and stores them into a configuration file

* Extractdata pulls down data in a CSV format, and writes out all queries used by each orgid

* Writequery converts the existing queries into a cleaner format, and annotates each query

NOTE: each of the scripts support using a '-h' to display help

To Do List:
===========

* Extend the pickle file information for the content

* add wrapper for exporting queries into a HTML tree and other components

License
=======

Copyright 2020 Wayne Kirk Schmidt
https://www.linkedin.com/in/waynekirkschmidt

Licensed under the Apache 2.0 License (the "License");

You may not use this file except in compliance with the License.
You may obtain a copy of the License at

    license-name   APACHE 2.0
    license-url    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Support
=======

Feel free to e-mail me with issues to: 

*   wschmidt@sumologic.com

*   wayne.kirk.schmidt@gmail.com

I will provide "best effort" fixes and extend the scripts.

Famous Libraries
================

[Famous Libraries of the World](http://www.mastersinlibraryscience.net/25-most-famous-libraries-of-the-world/)

