import unittest
from library_app.redis.redis_library import RedisLibrary
from library_app.library_test import LibraryTest


class RedisLibraryTest(LibraryTest, unittest.TestCase):

    def setUpClient(self):
        self.client = RedisLibrary()
