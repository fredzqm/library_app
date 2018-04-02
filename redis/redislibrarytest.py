import unittest
from redislibrary import *
from lib.librarytest import LibraryTest

class RedisLibraryTest(LibraryTest, unittest.TestCase):

	def setUpClient(self):
		self.client = RedisLibrary()
		get_redis().flushall()
		super(LibraryTest, self).setUp()

if __name__=='__main__':
	unittest.main()