# coding: utf-8
from distutils.core import setup

from setuptools import find_packages

scoop_packages = find_packages('.')

setup(
    name='scoop',
    version='2015.4.15',
    packages=scoop_packages,
    url='',
    license='',
    author='Steve Kossouho',
    author_email='steve.kossouho@gmail.com',
    description='The django scoop project by artscoop'
)
