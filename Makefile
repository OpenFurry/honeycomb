APPLICATIONS := activitystream administration core promotion publishers social submissions usermgmt
APPLICATIONS_COMMA := $(shell echo $(APPLICATIONS) | tr ' ' ',')

.PHONY: run
run:
	tox -e devenv

.PHONY: migrate
migrate: makemigrations
	venv/bin/python manage.py migrate

.PHONY: makemigrations
makemigrations: venv/bin/django-admin
	venv/bin/python manage.py makemigrations

.PHONY: fixtures
fixtures: venv/bin/django-admin
	venv/bin/python manage.py loaddata core/fixtures/*

.PHONY: generatefixtures
generatefixtures: venv/bin/django-admin
	venv/bin/python manage.py dumpdata flatpages -o core/fixtures/flatpages.json

.PHONY: reestdb
resetdb:
	- rm db.sqlite3
	$(MAKE) migrate fixtures

.PHONY: cleanmigrations
cleanmigrations: venv/bin/django-admin
	@echo "XXX HOLD UP - PRE-ALPHA STUFF ONLY XXX"
	@echo
	@echo "In case @makyo does not delete this before first alpha, do not"
	@echo "run this target.  Migrations are hecka important for dev after"
	@echo "that point!"
	@exit 1 # We really shouldn't do this, but may need to in the future
	@echo
	@echo "Psst, @makyo, don't forget to delete this target!"
	@sleep 5
	for i in $(APPLICATIONS); do \
		rm $$i/migrations/*.py; \
		touch $$i/migrations/__init__.py; \
	done

.PHONY: test
test:
	tox

.PHONY: testone
testone:
	tox -e 3.5

.PHONY: test-travis
test-travis:
	flake8
	coverage run \
		--source='$(APPLICATIONS_COMMA)' \
		--omit='*migrations*,*urls.py,*apps.py,*admin.py,*__init__.py,*test.py' \
		manage.py test --verbosity=2
	coverage report -m --skip-covered

.PHONY: clean
clean:
	rm -rf venv .tox
	find . -name *.py[co] -exec rm {} \;

.PHONY: deps
deps: venv
	venv/bin/pip install -r requirements.txt

venv:
	virtualenv venv
