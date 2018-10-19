
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


# Classy 
A metadata classification repository for tracking and auditing purposes  

## Technology Stack Used
Python 3 (Django)  
Initially built for MySQL, currently being ported to PostgreSQL  

## Getting Started  
These instructions will help you get a quick copy of the project up and running for development and testing purposes. See deployment if you want more in-depth setup instructions  
  
# Prerequisites  
Install system dependencies  
'''sh  
$ sudo apt-get install python3  
//If you are using a MySQL DB install a connector  
$ sudo apt-get install mysqlclient    
'''  
  
#Installing  
  
Clone github repo  
'''
$ git clone https://github.com/Krocodial/classy.git <project directory>  
'''

Navigate to repo  
'''  
$ cd <project directory>  
'''

Edit the configuration file  
'''
$ vi dsc/settings.py  
'''
Change USE_MYSQL_DB to 'True' if you are using a MYSQL DB, set it to 'False' if you want to use a SQLite DB.   
  
If you change it to 'True' you will need to load the database credentials into the environment variables. The python dot-env library is currently used to load the credentials into memory from a hidden file in the project directory.  
  
Make sure the variables with the corresponding names in the configuration file are base64 encoded and placed within the '.env' file in the project directory, these will then be auto-loaded by the app on startup.  
  
WARNING: ensure this file is excluded from version control and limit the permissions so that only the owner of the file may read it. Failure to do so may result in a compromised DB.  
  
Set BYPASS_AUTH to True  
Set Debug to False unless you wish to expose debug information  
  
Run setup script  
'''
$ chmod +x setup.sh    
$ ./setup.sh  
'''

This will create a virtual environment, install all python dependencies inside of it, then run the included tests with a coverage report.  
  
Finally run the development server  
'''
$ source envs/bin/activate  
$ python manage.py runserver <host>:<port>  
'''

Congratz! You now have a running metadata classification repo  

## Project Status
Release 1.0  

## Deployment (Local Development)

An example of this process on Ubuntu is included in bash script 'install.sh'  
  
Using apt or another package manager install  
*libmysqlclient-dev  
*python3-venv  
*python3-pip  
*apache2  
*apache2-dev  
*libapache2-mod-wsgi-py3  
  
* Create a virtual environment, 'python -m venv envs'.  
   
* Activate this virtual environment 'source /envs/bin/activate'.  
  
* Install local dependencies. 'pip install -r requirements.txt'.  
  
* Create environment variables with corresponding variable names in '.envs' in the project directory. These include your database credentials, secret, and host IP.  
  
* Customize the dsc/settings.py file. This includes changing the database connections, and ensuring that debug mode is turned off. If in-doubt follow the instructions included in this file.  
  
* Create a configuration based on the projects location for apache2, eg in /etc/apache2/sites-available. See the Django docs about deploying, they are very detailed.  
 
## Running Tests
  
Tests are built using Django's testing libraries. Navigate to the project directory and run the tests via 'python manage.py test' once in the virtual environment. If the application is not setup correctly this will now work. The tests are included in the project directory, with the prefix 'test'.  
 

## Security  
Authentication can be handled by SiteMinder or alternatively Django's built-in authentication by changing the BYPASS_AUTH variable in the settings file.  

Authorization is a customization of Django's provided authorization functionality. This allows segmentation of data as well as user authorization.  

Policies for use will be provided by the FLNR security team.  

## Files in this repository
Note: This is just a directory tree.  
```
classy/	
├── classy			-The app itself, model definitions, views, templates, scripts, etc.
│   ├── migrations		-Here are the migrations for our DB
│   │   └── __pycache__
│   ├── __pycache__
│   ├── static
│   │   └── classy
│   └── templates
│       └── classy
├── dsc				-Configuration information
│   └── __pycache__
├── envs			-Contains our virtual environment, as well as the admin pages
│   ├── bin
│   │   └── __pycache__
│   ├── include
│   ├── lib
│   │   └── python3.5
│   ├── lib64 -> lib
│   └── share
│       └── python-wheels
└── static			-Static files for our webserver
    ├── admin
    │   ├── css
    │   ├── fonts
    │   ├── img
    │   └── js
    └── classy
        ├── css
        ├── images
        └── js
```

## Getting Help or Reporting an Issue

To report bugs/issues/feature requests, please file an [issue](../../issues).

## How to Contribute

If you would like to contribute, please see our [CONTRIBUTING](./CONTRIBUTING.md) guidelines.

Please note that this project is released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). 
By participating in this project you agree to abide by its terms.

## License

    Copyright 2016 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
