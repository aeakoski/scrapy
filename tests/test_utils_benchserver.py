import unittest

import scrapy
from scrapy.utils.benchserver import _getarg

class MockRequest:
    def __init__(self, args):
        self.args = args

class BenchserverTest(unittest.TestCase):
    def setUp(self):
        mockargs = {'name':[1]}
        self.mockrequest = MockRequest(mockargs)

    def test_type(self):
        self.assertEqual(_getarg(self.mockrequest, 'name'), '1')

    def test_default(self):
        self.assertEqual(_getarg(self.mockrequest, 'none', default='default'), 'default')
