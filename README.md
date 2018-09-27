
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


# DSC (Data Security Classification)
An easy to use GUI that allows users to view/edit/create centralized classified data

## Technology Stack Used
Python 3 (Django)  
Full support for most DBs, this was built for MySQL so PostgreSQL will work flawlessly as well  

## Third-Party Products/Libraries used and the the License they are covered by
mysqlclient  
Django
python-dotenv

## Project Status
Stable  

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
