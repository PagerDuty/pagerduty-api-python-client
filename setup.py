#!/usr/bin/env python
from setuptools import setup, find_packages

with open('pypd/version.py') as version_file:
    exec(compile(version_file.read(), version_file.name, 'exec'))

options = {
    'name': 'pypd',
    'version': __version__,
    'packages': find_packages(),
    'scripts': [],
    'description': 'A python client for PagerDuty API',
    'author': 'JD Cumpson',
    'author_email': 'jdc@pagerduty.com',
    'maintainer_email': 'jdc@pagerduty.com',
    'license': 'MIT',
    'url': 'https://github.com/PagerDuty/pypd',
    'download_url': 'https://github.com/PagerDuty/pypd/archive/master.tar.gz',
    'classifiers': [
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    'install_requires': ['ujson', 'requests'],
    'tests_require': [],
    'cmdclass': {}
}

setup(**options)
