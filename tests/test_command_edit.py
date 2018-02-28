from twisted.trial import unittest

from scrapy.utils.testsite import SiteTest
from scrapy.utils.testproc import ProcessTest

from scrapy.commands.edit import Command

class FetchTest(ProcessTest, SiteTest, unittest.TestCase):

    def test_edit_command_syntax(self):
        "condition: Command should return the correct syntax"
        command = Command()
        self.assertEqual(command.syntax(), "<spider>")
