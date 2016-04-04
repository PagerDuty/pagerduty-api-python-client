
from os.path import dirname, join

import pypd


def preload():
    path = join(dirname(dirname(dirname(__file__))), 'api.key')
    with open(path, 'r+b') as f:
        pypd.api_key = f.read()
