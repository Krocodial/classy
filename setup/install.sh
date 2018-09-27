
echo 'initializing'
sudo apt-get install libmysqlclient-dev python3-venv python3-pip python3 apache2 apache2-dev libapache2-mod-wsgi-py3
python3 -m venv envs
source envs/bin/activate
pip install -r requirements.txt
python3 manage.py test
