#!/bin/bash

percent=`venv/bin/coverage report|tail -n 1|perl -ple 's/\s+/:/g'|cut -d : -f 4`
number=`echo "$percent" | tr -d '%'`

if [ "$number" -gt 95 ] ; then
    color='brightgreen'
elif [ "$number" -gt 90 ] ; then
    color='green'
elif [ "$number" -gt 85 ] ; then
    color='yellowgreen'
else
    color='red'
fi

badge="https://img.shields.io/badge/coverage-"$percent"25-"$color".svg"

cat README.md \
    | perl -ple 's#https://img.shields.io/badge/coverage-\d+%25-\w+.svg#'$badge'#' \
    > README.new

mv README.new README.md
