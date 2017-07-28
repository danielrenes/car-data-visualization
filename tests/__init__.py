import sys
import unittest

def run():
    tests = unittest.TestLoader().discover('.')
    ok = unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful()
    sys.exit(0 if ok else 1)
