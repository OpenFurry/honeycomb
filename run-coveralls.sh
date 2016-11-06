#!/bin/bash

if [ "$TRAVIS_PYTHON_VERSION" == "3.5" ] ; then
    coveralls
fi
