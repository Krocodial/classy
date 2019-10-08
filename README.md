
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


# Classy 
A metadata classification repository for tracking and auditing purposes  

## Status
  
Release 2.0.0 
  
## Technology Stack Used
Python ~3.6 (Django)  
PostgreSQL 9.6 (or latest)  
NGINX 1.15.12  
ModSecurity v3.2  

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
$ vi project/settings.py  
```  
Make sure the variables with the corresponding names in the configuration file are base64 encoded and placed within the '.env' file in the project directory, these will then be auto-loaded by the app on startup.  
  
WARNING: ensure this file is excluded from version control and limit the permissions so that only the owner of the file may read it. Failure to do so may result in a compromised DB.  

```sh
python3 -m venv envs  
source envs/bin/activate  
pip install -r requirements.txt  
set -a  
. .env  
set +a  
export POSTGRESQL_SERVICE_HOST=localhost  
``` 
 
To provide file handling functionality, as well as other long-running process' django-background tasks is used. Tasks will be created and registered for the user automatically. However, to actually run these tasks a simple cron job must be setup.  
  
Using Crontab -e the following is all you need to do:  
```  
*/1 * * * * /usr/bin/flock -n /tmp/QRH7mA40aRL2NVyVUbcH.lockfile python ~/manage.py process_tasks --queue=uploader
*/1 * * * * /usr/bin/flock -n /tmp/uj5l6n7iAGtM8gx9fNuo.lockfile python ~/manage.py process_tasks --queue=counter 
```  
  
Flock will need to be installed to allow the creation and management of locks, preventing process bombs.  
  
Change the path at the end of each to correspond to the project directory, and modify the scripts accordingly. All they do is navigate to the project directory, activate the virtual env, and run the command 'python manage.py process_tasks --queue <queue>'  
    

Finally run the development server  
```sh  
$ source envs/bin/activate  
$ python manage.py runserver <host>:<port> 
$ python manage.py process_tasks (if no cronjob is setup)   
```  

Congratulations! You now have a running security classification repository  

# Deployment  

For local deployment in docker containers the steps are fairly easy.  

Ensure docker is installed and configured correctly.  
Then:  
```sh
docker run -p 0.0.0.0:5432:5432 -e POSTGRES_PASSWORD=docker -d postgres  
git clone https://github.com/krocodial/classy .  
docker build -t classy --no-cache .  
docker run -p 0.0.0.0:8080:8080 --env-file .env -d classy  
cd conf  
docker build -t nginx-proxy --no-cache .  
docker run -p 0.0.0.0:1337:1337  --env-file .env -d nginx-proxy  
```
  
It should be noted that no cronjob runs by default, which means aggregate stats, and file upload handling won't be on by default. To remedy this fire up another shell and do the following.  
```sh
docker container ls  
docker exec -it <container-name> /bin/bash  
python manage.py process_tasks  
```  
  
Now you have a local development deployment of classy up and running.  
  
## Backing up
  
Default Django flows can be used to backup data.  
```  
python manage.py dumpdata --exclude=auth.permission --exclude=auth.group --exclude=contenttypes > <backup file>.json  
./oc rsync <pod>:/path/to/backup.json /local/dir/to/backup/to  
```
  
## Running Tests
  
Tests are built using Django's testing libraries. Once in the virtual environment (source envs/bin/activate), navigate to the project directory and run the tests via 'python manage.py test tests/'. If the application is not setup correctly this will not work.   
  

## Security  
Authentication is provided via the bcgov keycloak service. The Authorization flow is used, with checks to allow immediate revocation in the event of account compromise. By default user accounts are denied any access to this tool.  

Authorization is very granular for classification access, allowing business areas to only access what they are in charge of. Users can also be granted over-arching access to functionality based on Django's default authorization flow.  



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
