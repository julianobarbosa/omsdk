#!/bin/sh
rm -fr build dist omsdk.egg-info
#cp setup-linux.py setup.py
#python setup.py sdist --formats=gztar
echo "$1.$2" > _version.txt
python setup-omdrivers.py bdist_wheel --universal
python setup-omsdk.py bdist_wheel --universal
rm -Rf _version.txt
rm -Rf build
rm -Rf omsdk.egg-info
#python setup.py bdist_egg
#rm -Rf build
#rm -Rf omsdk.egg-info
