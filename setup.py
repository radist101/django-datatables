#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='datatables',
    version='0.0.1',
    description='Port between datatables and django',
    url='https://github.com/radist101/django-datatables',
    author='rdst101@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=(
        'django',
    ),
)
