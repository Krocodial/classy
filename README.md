
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


# DSC (Data Security Classification)
An easy to use GUI that allows users to view/edit/create centralized classified data

## Technology Stack Used
Django, and POSTgres. Although will soon be migrated to MySQL  
Django==2.0.1  
Python==3.5  

## Third-Party Products/Libraries used and the the License they are covered by
psycopg2==2.7.3.2 -- (http://initd.org/psycopg/license/)  
pytz==2017.3 -- Covered by the MIT license (https://pypi.python.org/pypi/pytz)  

## Project Status
In-Development  

## Documentation

GitHub Pages (https://guides.github.com/features/pages/) are a neat way to document you application/project.

## Security  
Authentication & Authorization are handled by Django's built in security. However once this project progresses it will be modified to use the existing Authenication process. 

Policies for use will be provided by the FLNR security team.  

## Files in this repository

```
classy/         - Main project folder
└── views.py        
└── models.py         

dsc/		- Setup folder

dsc_env/	- Directory for our virtual environment dependencies
```

## Deployment (Local Development)

* Since all dependencies are contained in a virtualenv the only requirement is to be able to activate this localized environment. See (https://virtualenv.pypa.io/en/stable/) for setup instructions. Command to activate the environment is 'source dsc_env/bin/activate')

* Edit the dsc/settings.py file to include your secret, database connection credentials, and allowed hosts

* Once in the virtual environment run the server with 'python3 manage.py runserver host:port'


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
