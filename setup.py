#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='envaya',
    version='0.0.4',
    description='Tiny envaya utility',
    author='Mitchel Kelonye',
    author_email='kelonyemitchel@gmail.com',
    url='https://github.com/kelonye/django-envaya',
    requires=[
          'Django (>=1.3.0)'
        , 'pytz'
    ],
    packages=find_packages(),
    license='MIT License',
    zip_safe=True)
