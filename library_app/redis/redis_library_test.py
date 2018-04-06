import unittest

from library_app.library_test import LibraryTest
from library_app.redis.redis_library import RedisLibrary


class RedisLibraryTest(LibraryTest, unittest.TestCase):

    def setUpClient(self):
        self.client = RedisLibrary()
