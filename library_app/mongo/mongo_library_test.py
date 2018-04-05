import unittest
from .mongo_library import MongoLibrary
from library_app.library_test import LibraryTest


@unittest.skip('')
class MongoLibraryTest(LibraryTest, unittest.TestCase):

    def setUpClient(self):
        self.client = MongoLibrary()
