
build:
<<<<<<< HEAD
	sudo service apache2 stop
=======
	sudo service <apache_instance> stop
>>>>>>> 4ae3ddc16cb17e3c7c8091a5a9cfb757c6935700
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py collectstatic --noinput
	python3 manage.py check --deploy
	python3 manage.py test
<<<<<<< HEAD
	sudo service apache2 start

restart:
	sudo service apache2 restart

run:
	python3 manage.py runserver 0.0.0.0:1337
=======
	sudo service <apache_instance> start

restart:
	sudo service <apache_instance> restart

run:
	python3 manage.py runserver localhost:1337
>>>>>>> 4ae3ddc16cb17e3c7c8091a5a9cfb757c6935700

