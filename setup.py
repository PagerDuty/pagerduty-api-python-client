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
    'maintainer': 'JD Cumpson',
    'maintainer_email': 'abrooks@pagerduty.com',
    'license': 'MIT',
    'url': 'https://github.com/PagerDuty/pagerduty-api-python-client',
    'download_url': 'https://github.com/PagerDuty/pagerduty-api-python-client/archive/master.tar.gz',
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    'install_requires': ['requests', 'six'],
    'tests_require': [],
    'cmdclass': {}
}

setup(**options)
