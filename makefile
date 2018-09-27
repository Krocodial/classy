
build:
	sudo service <apache_instance> stop
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py collectstatic --noinput
	python3 manage.py check --deploy
	python3 manage.py test
	sudo service <apache_instance> start

restart:
	sudo service <apache_instance> restart

run:
	python3 manage.py runserver localhost:1337

