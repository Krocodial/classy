
build:
	sudo service apache2 stop
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py collectstatic --noinput
	python3 manage.py check --deploy
	python3 manage.py test
	sudo service apache2 start

restart:
	sudo service apache2 restart

run:
	python3 manage.py runserver 0.0.0.0:1337

