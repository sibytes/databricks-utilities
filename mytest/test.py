import unittest
import sys, os
from utilities import add

class Test(unittest.TestCase):

    def test_add(self):
      self.assertEqual(add(2,2), 4)
      

            
def run_tests():
  unittest.main(argv=[''], verbosity=2, exit=False)