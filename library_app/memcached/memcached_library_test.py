import unittest

from library_app.library_test import LibraryTest
from .memcached_library import MemcachedLibrary


class MemCachedLibraryTest(LibraryTest, unittest.TestCase):

    def setUpClient(self):
        self.client = MemcachedLibrary()
