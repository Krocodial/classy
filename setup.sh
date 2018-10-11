python3 -m venv envs
source envs/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
deactivate
./tests/test.sh
