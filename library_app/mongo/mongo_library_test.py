import unittest

from library_app.library_test import LibraryTest
from .mongo_library import MongoLibrary


class MongoLibraryTest(LibraryTest, unittest.TestCase):

    def setUpClient(self):
        self.client = MongoLibrary()
