import unittest
from lib.redis.library import get_redis, RedisLibrary
from lib.library_test import LibraryTest

class RedisLibraryTest(LibraryTest, unittest.TestCase):

	def setUpClient(self):
		self.client = RedisLibrary()
		get_redis().flushall()
		super(LibraryTest, self).setUp()

