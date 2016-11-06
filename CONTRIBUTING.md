Contributing
------------

## Issues

File them :)

## Process

1. Fork the code to your own repository and clone it to your local machine.
2. Check out a feature branch:

   `git checkout -b my_feature`
3. Work work work...
    1. You can run the development server with `make run`.
    2. If you need a different port or anything, you can run it by hand with
       `venv/bin/python manage.py runserver [options]`.
4. Commit and push your feature branch
5. Create a pull request against OpenFurry/honeycomb, describing what you've
   done and, if needed, providing QA instructions.  CI will run automatically on
   PRs and any future commits to them.
6. If CI passes and you get one "approve" review and "QA OK", someone will
   land your branch for you (ping @makyo if need be).
7. If not, address the comments and commit your changes, then ping for a
   re-review.

## Tests

* Ensure test coverage (total and per module) stays above 90%.  If it falls
  below for any reason, make sure that tests are stubbed out and skipped
  with `@unittest.skipIf` or `@unittest.skipUnless` with a provided reason
  explaining why.
* Testing is done through tox and can take some time due to the multiple
  environments involved.  To that end, tests are run in parallel if possible, with as many threads as your computer has cores.  There are [some limitations](https://docs.djangoproject.com/en/1.10/ref/django-admin/#cmdoption-test--parallel) around this, but tests *should* Just Work all the same.
* Additionally, the default `test` make target runs tests only on py3.5.  `testall` will run tests on all environments.
* Tests are run with the `django-nose` testrunner, so you can use any nose
  options with the test command. `venv/bin/python manage.py test --help` for
  more information.  `--nologcapture` is suggested, as Markdown.py is rather chatty.

  For example, you may run just one test suite with `venv/bin/python manage.py test --nologcapture social.tests` or just one case with `venv/bin/python manage.py test --nologcapture social.tests:TestPostCommentView`.

## Style

Python:

* flake8 (PRs will be linted, running `make test` will also lint)
* All `TODO` style comments should be followed on the next line with a comment: `# @<github username> YYYY-MM-DD #<github issue number>`.
* All `XXX` style comments should come with adequate justification, and a link if possible.

Templates:

* 4 space indent
* Indent inside Django block tags except root-level `block` tags
* Indent inside all elements (Including `<p>` and `<li>`, which vim will not do
  by default) unless they are on one line.
* No line-length limit

Markdown:

* 4 space indent
* Continued lines in lists indented so that the first character is vertically
  in line with the first character (not list item signifier) on previous
  line.  See the source of this doc for examples.
