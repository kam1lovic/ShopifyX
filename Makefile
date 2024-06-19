mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

admin:
	python3 manage.py createsuperuser

start:
	python3 main.py & python3 manage.py runserver


