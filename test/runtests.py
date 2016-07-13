# Copyright (c) PagerDuty.
# See LICENSE for details.

if __name__ == '__main__':
    import os.path
    import unittest
    import argparse

    dirname = os.path.dirname(__file__)

    parser = argparse.ArgumentParser(description='Run tests for pypd')
    parser.add_argument('--verbose', '-v', action='count', dest='verbosity',
                        default=1)

    args = parser.parse_args()
    suite = unittest.TestLoader().discover(dirname, pattern='*.py')
    unittest.TextTestRunner(verbosity=args.verbosity).run(suite)
