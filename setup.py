"""
Project setup
"""

from setuptools import setup, find_packages

setup(
    name='distributed-lab-4',
    version='0.0.1',
    description='Lab 4 in distributed systems',
    author='Fredrik Rahn & Branne Branzell',
    packages=find_packages(exclude=('tests', 'docs'))
    )
