#!/bin/bash

percent=`venv/bin/coverage report|tail -n 1|perl -ple 's/\s+/:/g'|cut -d : -f 4`
badge="https://img.shields.io/badge/coverage-"$percent"25-lightgrey.svg"
cat README.md | perl -ple 's#https://img.shields.io/badge/coverage-\d+%25-lightgrey.svg#'$badge'#' > README.new
mv README.new README.md
