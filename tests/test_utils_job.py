import os
import unittest

import scrapy
from scrapy.utils.job import job_dir

class JobTest(unittest.TestCase):
    temp_dir_name = 'temp_test_job'

    def setUp(self):
        self.mocksettings = {'JOBDIR':self.temp_dir_name}

    def test_dir_created(self):
        if os.path.exists(self.temp_dir_name):
            os.rmdir(self.temp_dir_name)

        job_dir(self.mocksettings)
        assert os.path.exists(self.temp_dir_name)

        os.rmdir(self.temp_dir_name)
        assert not os.path.exists(self.temp_dir_name)
