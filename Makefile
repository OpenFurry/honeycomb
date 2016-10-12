.PHONY: run
run: venv/bin/django-admin
	venv/bin/python manage.py runserver 0.0.0.0:8000

.PHONY:
test: venv/bin/django-admin
	venv/bin/python manage.py test

.PHONY: clean
clean:
	rm -rf .venv
	find . -name *.py[co] -exec rm {} \;

.PHONY: deps
deps: venv
	venv/bin/pip install -r requirements.txt

venv:
	virtualenv venv

