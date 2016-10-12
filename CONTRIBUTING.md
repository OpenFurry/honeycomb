Contributing
------------

## Process

1. Fork the code to your own repository and clone it to your local machine.
2. Check out a feature branch:

   `git checkout -b my_feature`
3. Work work work...
4. Commit and push your feature branch
5. Create a pull request against OpenFurry/honeycomb, describing what you've
   done and, if needed, providing QA instructions.  CI will run automatically on
   PRs and any future commits to them.
6. If CI passes and you get one "approve" review and "QA OK", someone will land
   your branch for you (ping @makyo if need be).
7. If not, address the comments and commit your changes, then ping for a
   re-review.

## Style

Python:

* flake8 (PRs will be linted, check yourself with `make lint`)

Templates:

* 4 space indent
* Indent inside Django block tags
* Indent inside all elements (Including `<p>` and `<li>`, which vim will not do
  by default) unless they are on one line.
* No line-length limit

Markdown:

* 4 space indent
* 80 character line-length limit
* Continued lines in lists indented so that the first character is vertically in
  line with the first character (not list item signifier) on previous line.  See
  the source of this doc for examples.

## Caveats

Do not commit `db.sqlite3` unless you really mean to (i.e: you've made a db
change resulting in a migration).  This is to help new developers get started
easily so that there's not garbage data in the dev database.  To help keep
yourself from doing this, you can set a pre-commit hook to warn you.

I.e: set `.git/hooks/pre-commit` to:

```shell
#!/bin/sh

if git rev-parse --verify HEAD >/dev/null 2>&1
then
	against=HEAD
else
	# Initial commit: diff against an empty tree object
	against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# Redirect output to stderr.
exec 1>&2

if [ "$UPDATEDB" != "true" ] &&
    [ "$(git status -s db.sqlite3)" != "" ]
then
	cat <<\EOF
Error: Attempting to commit the dev database without the UPDATEDB flag.

If you have made changes to the development database schema that need to
be committed with your branch, please reset the database and commit with
the UPDATEDB flag set

  make resetdb
  UPDATEDB=true git config hooks.allownonascii true
EOF
	exit 1
fi
```
