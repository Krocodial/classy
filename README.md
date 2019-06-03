
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


# Classy 
A metadata classification repository for tracking and auditing purposes  

## Status
  
Release 2.0.0 
  
## Technology Stack Used
Python ~3.6 (Django)  
PostgreSQL 9.6 (or latest)  

## Getting Started  
These instructions will help you get a quick copy of the project up and running for development and testing purposes. See deployment if you want more in-depth setup instructions  
  
## Prerequisites 
You'll need an instance of OpenShift currently running. The current project hardware requests are 8 cores, 32GBs RAM, and 200GB persistant storage per project space.  

Go through the Jenkinsfile in the project root directory and modify the global values accordingly. The most important will be the namespace.   
   
This setup assumes you have Jenkins and a SonarQube instance running in your TOOLS environment. If these are missing you can always remove the SAST/DAST functions from the Jenkinsfile, although I can't recommend this.  
# Initial Setup
  

Clone github repo  
```sh  
$ git clone https://github.com/Krocodial/classy.git <project directory>  
```   
  
Navigate to repo  
```sh  
$ cd <project directory>  
```  
  
Edit the configuration file  
```sh  
$ vi dsc/settings.py  
```  
Change USE_MYSQL_DB to 'True' if you are using a MYSQL DB, set it to 'False' if you want to use a SQLite DB.   
  
If you change it to 'True' you will need to load the database credentials into the environment variables. The python dot-env library is currently used to load the credentials into memory from a hidden file in the project directory.  
  
Make sure the variables with the corresponding names in the configuration file are base64 encoded and placed within the '.env' file in the project directory, these will then be auto-loaded by the app on startup.  
  
WARNING: ensure this file is excluded from version control and limit the permissions so that only the owner of the file may read it. Failure to do so may result in a compromised DB.  
  
Set BYPASS_AUTH to True  
Set Debug to False unless you wish to expose debug information  
  
Run setup script  
```sh  
$ chmod +x setup.sh    
$ ./setup.sh  
```  

This will create a virtual environment, install all python dependencies inside of it, then run the included tests with a coverage report.  
  
  
To provide file handling functionality, as well as other long-running process' django-background tasks is used. Tasks will be created and registered for the user automatically. However, to actually run these tasks a simple cron job must be setup.  
  
Using Crontab -e the following is all you need to do:  
```  
*/1 * * * * /usr/bin/flock -n /tmp/QRH7mA40aRL2NVyVUbcH.lockfile ~/crontab/file_handler.sh  
*/1 * * * * /usr/bin/flock -n /tmp/uj5l6n7iAGtM8gx9fNuo.lockfile ~/crontab/count_handler.sh  
```  
  
Flock will need to be installed to allow the creation and management of locks, preventing process bombs.  
  
Change the path at the end of each to correspond to the project directory, and modify the scripts accordingly. All they do is navigate to the project directory, activate the virtual env, and run the command 'python manage.py process_tasks --queue <queue>'  
    

Finally run the development server  
```sh  
$ source envs/bin/activate  
$ python manage.py runserver <host>:<port>  
```  

Congratz! You now have a running metadata classification repo  

# Deployment  
  
Once the steps in 'Initial Setup' are complete follow this section to find out how to serve classy using a webserver.    
  
Using apt or another package manager   
```sh  
$ sudo apt-get install libmysqlclient-dev python3 python3-venv python3-pip apache2 apache2-dev libapache-mod-wsgi-py3  
```
  
Create a configuration based on the projects location for apache2, eg in /etc/apache2/sites-available. An example apache virtualhost configuration file in included in tests/config_example  
  
Modify the dsc/settings.py file. An example file, as well as comments describing the different options available in the settings file is included in the tests/settings_example file  
  
 
## Running Tests
  
Tests are built using Django's testing libraries. Once in the virtual environment (source envs/bin/activate), navigate to the project directory and run the tests via 'python manage.py test'. If the application is not setup correctly this will not work.   
  
Note: The tests will automatically run if the 'setup.sh' script is run. Thus they are included only for development purposes to make sure you do not mess anything up.     
  

## Security  
Authentication can be handled by SiteMinder or alternatively Django's built-in authentication by changing the BYPASS_AUTH variable in the settings file.  

Authorization is a customization of Django's provided authorization functionality. This allows segmentation of data as well as user authorization.  

Policies for use will be provided by the FLNR security team.  

tes

## Files in this repository  
```sh  
classy/
├── classy
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── scripts.py
│   ├── static
│   │   ├── admin
│   │   └── classy
│   ├── templates
│   │   ├── admin
│   │   └── classy
│   ├── templatetags
│   │   └── classy_extras.py
│   ├── urls.py
│   └── views.py
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── dsc
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── LICENSE
├── manage.py
├── README.md
├── requirements.txt
├── setup.sh
└── tests
    ├── __init__.py
    ├── test_func.py
    ├── test_model.py
    ├── test.sh
    └── test_view.py

```

## Getting Help or Reporting an Issue

To report bugs/issues/feature requests, please file an [issue](../../issues).

## How to Contribute

If you would like to contribute, please see our [CONTRIBUTING](./CONTRIBUTING.md) guidelines.

Please note that this project is released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). 
By participating in this project you agree to abide by its terms.

## License

    Copyright 2018 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
