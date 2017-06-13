# Copyright (c) PagerDuty.
# See LICENSE for details.
from os.path import dirname, join

import pypd


def preload():
    path = join(dirname(dirname(dirname(__file__))), 'api.key')
    pypd.set_api_key_from_file(path)
