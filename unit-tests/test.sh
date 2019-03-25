source envs/bin/activate
coverage run --source='classy' manage.py test
echo '-----Coverage Report-----'
coverage report
python3 manage.py check
deactivate
rm .coverage
