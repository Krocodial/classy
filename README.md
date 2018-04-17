
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


# DSC (Data Security Classification)
An easy to use GUI that allows users to view/edit/create centralized classified data

## Technology Stack Used
Django, and POSTgres. Although will soon be migrated to MySQL  
Django==2.0.1  
Python==3.5.2  

## Third-Party Products/Libraries used and the the License they are covered by
psycopg2==2.7.3.2 -- (http://initd.org/psycopg/license/)  
pytz==2017.3 -- Covered by the MIT license (https://pypi.python.org/pypi/pytz)  
mysqlclient  
libmysqlclient-dev  
python3-venv  
python3-pip  
apache2  
apache2-dev  
libapache2-mod-wsgi-py3  
(or another HTTP server with python 3 interface)  

## Project Status
In-Development  

## Documentation

GitHub Pages (https://guides.github.com/features/pages/) are a neat way to document you application/project.

## Security  
Authentication & Authorization are handled by Django's built in security. However once this project progresses it will be modified to use the existing Authenication process. 

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

## Deployment (Local Development)

Using apt or another package manager install  
*libmysqlclient-dev  
*python3-venv  
*python3-pip  
*apache2  
*apache2-dev  
*libapache2-mod-wsgi-py3  

* Since the rest of the dependencies are contained in a virtual environment the only requirement is to be able to activate this localized environment. See (https://virtualenv.pypa.io/en/stable/) for setup instructions. Command to activate the environment is 'source env/bin/activate')

* Create environment variables with corresponding variable names in dsc/settings.py. These include you database credentials, secret, and host IP  

* Create a configuration based on the projects location for apache2, eg in /etc/apache2/sites-available. See the Django docs about deploying, they are very detailed.  


## Deployment (OpenShift)

See (openshift/Readme.md)

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
