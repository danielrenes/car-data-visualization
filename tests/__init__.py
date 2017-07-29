import sys
import unittest

def run():
    tests = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful()
