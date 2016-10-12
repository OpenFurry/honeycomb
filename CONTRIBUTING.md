Contributing
------------

## Style

* flake8

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
