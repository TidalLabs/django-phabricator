#!/usr/bin/env python
import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

readme = open('README.rst').read()

requirements = [
    'django>=1.7',
    'django-model-utils>=2.2',
    'phabricator',
    'pytz',
]

extras = {
    'develop': ['mock'],
}

setup(
    name='django-phabricator',
    version='0.1',
    description='Phabricator tools for Django, with an emphasis on analytics',
    long_description=readme + '\n\n',
    author='Noemi Millman',
    author_email='noemi@tid.al',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras,
    license="BSD",
    zip_safe=False,
)
