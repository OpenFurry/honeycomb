APPLICATIONS := activitystream administration core promotion publishers social submissions tags usermgmt
APPLICATIONS_COMMA := $(shell echo $(APPLICATIONS) | tr ' ' ',')
TESTTAGS_ARGS := $(shell echo $(TAGS) | xargs python -c 'import sys;print("--tag "+" --tag ".join(" ".join(sys.argv[1:]).split(",")))')

.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: run
run: ## Run the development environment from tox.
	tox -e devenv

.PHONY: shell
shell: ## Run the django shell using some additional tools.
	venv/bin/python manage.py shell_plus

.PHONY: migrate
migrate: makemigrations ## Run migrate on the DB, updating schema per migration files.
	venv/bin/python manage.py migrate
	$(MAKE) generatefixtures

.PHONY: makemigrations
makemigrations: venv/bin/django-admin ## Generate migration files based on models.
	venv/bin/python manage.py makemigrations

.PHONY: fixtures
fixtures: venv/bin/django-admin ## Load data fixtures.
	venv/bin/python manage.py loaddata core/fixtures/*

.PHONY: generatefixtures
generatefixtures: venv/bin/django-admin ## Generate data fixtures.
	venv/bin/python manage.py dumpdata --natural-foreign --natural-primary -o core/fixtures/flatpages.json flatpages.FlatPage
	venv/bin/python manage.py dumpdata --natural-foreign --natural-primary  -o core/fixtures/groups.json auth.Group auth.Permission

.PHONY: update-flatpages
update-flatpages: venv/bin/django-admin ## Update the flatpages from the markdown files.
	venv/bin/python manage.py update_flatpages
	venv/bin/python manage.py dumpdata --natural-foreign --natural-primary -o core/fixtures/flatpages.json flatpages.FlatPage

.PHONY: collectstatic
collectstatic: ## Collect static files into the STATIC_ROOT directory.
	venv/bin/python manage.py collectstatic

.PHONY: check
check: ## Run various checks against the project
	venv/bin/python manage.py check --deploy
	venv/bin/python manage.py validate_templates

.PHONY: reestdb
resetdb: ## Remove the development database and regenerate it, loading fixtures.
	- rm db.sqlite3
	$(MAKE) migrate fixtures

.PHONY: cleanmigrations
cleanmigrations: venv/bin/django-admin ## DO NOT USE: clean superfluous migrations.
	@echo "XXX HOLD UP - PRE-ALPHA STUFF ONLY XXX"
	@echo
	@echo "In case @makyo does not delete this before first alpha, do not"
	@echo "run this target.  Migrations are hecka important for dev after"
	@echo "that point!"
	exit 1 # We really shouldn't do this, but may need to in the future
	@echo
	@echo "Psst, @makyo, don't forget to delete this target!"
	@sleep 5
	for i in $(APPLICATIONS); do \
		rm $$i/migrations/*.py; \
		touch $$i/migrations/__init__.py; \
	done

.PHONY: update-revno
update-revno: venv/bin/django-admin ## Update the git revno for non-DEBUG templates.
	venv/bin/python manage.py git_revno $(TAG)

.PHONY: test
test: ## Rapid test (parallel test running, no coverage)
	tox -e rapidtest

.PHONY: testall
testall: ## Run tests in all available environments.
	tox

.PHONY: testone
testone: ## Run tests in py3.5 only.
	tox -e 3.5

.PHONY: testtags
testtags: ## Run only tests tagged with a certain tag or tags (comma separated) passed through the TAGS environment variable.
	venv/bin/python manage.py test --parallel --verbosity=2 $(TESTTAGS_ARGS)

.PHONY: test-travis
test-travis: ## Test target for travis-ci use.
	flake8
	coverage run \
		--source='$(APPLICATIONS_COMMA)' \
		--omit='*migrations*,*urls.py,*apps.py,*admin.py,*__init__.py,*test.py' \
		manage.py test --verbosity=2 $(TEST_SUITE)
	coverage report -m --skip-covered

.PHONY: metadata
metadata: ## Get metadata about the project (sloc, models, urls)
	git ls-files \
		| grep -v static \
		| grep -v manage.py \
		| grep -v migrations \
		| grep -E '(.py|.html|.md|Makefile|sh)' \
		| xargs python sloc.py > sloc.tsv
	venv/bin/python manage.py graph_models -a -o models.png
	venv/bin/python manage.py show_urls > urls.tsv

.PHONY: clean
clean: ## Remove virtualenv and tox environments, along with compiled/optimized python files.
	rm -rf venv .tox
	find . -name *.py[co] -exec rm {} \;

.PHONY: deps
deps: check-sysdeps venv ## Install dependencies in the virtualenv.
	venv/bin/pip install -r requirements.txt

.PHONY: check-sysdeps
check-sysdeps: ## Check that system dependencies are met.
	@printf "\e[31mChecking for tox...\e[0m"
	@tox --version
	@printf "\e[32m- tox found\e[0m\n\n"
	@printf "\e[31mChecking for virtualenv...\e[0m"
	@virtualenv --version
	@printf "\e[32m- virtualenv found\e[0m\n\n"
	@printf "\e[31mChecking for pandoc...\e[0m"
	@pandoc --version
	@printf "\e[32m- pandoc found\e[0m\n"
	@printf "\e[32mSysdeps met\e[0m\n"

venv: ## Setup the virtualenv.
	virtualenv venv
