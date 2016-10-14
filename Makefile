APPLICATIONS := admin app promotion publishers social submissions usermgmt

.PHONY: run
run: venv/bin/django-admin
	venv/bin/python manage.py runserver 0.0.0.0:8000

.PHONY: migrate
migrate: makemigrations
	venv/bin/python manage.py migrate

.PHONY: makemigrations
makemigrations: venv/bin/django-admin
	venv/bin/python manage.py makemigrations

.PHONY: reestdb
resetdb:
	- rm db.sqlite3
	$(MAKE) migrate

.PHONY: cleanmigrations
cleanmigrations: venv/bin/django-admin
	@echo "XXX HOLD UP - PRE-ALPHA STUFF ONLY XXX"
	@echo
	@echo "In case @makyo does not delete this before first alpha, do not"
	@echo "run this target.  Migrations are hecka important for dev after"
	@echo "that point!"
	@echo
	@echo "Psst, @makyo, don't forget to delete this target!"
	@sleep 5
	for i in $(APPLICATIONS); do \
		rm $$i/migrations/*.py; \
		touch $$i/migrations/__init__.py; \
	done

.PHONY: check
check: lint test

.PHONY:
test: venv/bin/django-admin
	venv/bin/python manage.py test
	
.PHONY: lint
lint: venv/bin/flake8
	venv/bin/flake8

.PHONY: clean
clean:
	rm -rf venv
	find . -name *.py[co] -exec rm {} \;

.PHONY: deps
deps: venv
	venv/bin/pip install -r requirements.txt

venv:
	virtualenv venv

