import unittest

from library_app.library_test import LibraryTest
from .neo4j_library import Neo4jLibrary


class Neo4jLibraryTest(LibraryTest, unittest.TestCase):

    def setUpClient(self):
        self.client = Neo4jLibrary()

    def test_rate1(self):
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 1)

        self.assertEqual(1, self.client.get_rating('zhangq1', '1'))

    def test_rate2(self):
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 5)

        self.assertEqual(5, self.client.get_rating('zhangq1', '1'))

    def test_rate_out_of_range1(self):
        self.client.checkout_book('zhangq1', '1')
        with self.assertRaises(Exception) as context:
            self.client.rate_book('zhangq1', '1', 0)
        self.assertEqual('rating_between_1_and_5', str(context.exception))

    def test_rate_out_of_range2(self):
        self.client.checkout_book('zhangq1', '1')
        with self.assertRaises(Exception) as context:
            self.client.rate_book('zhangq1', '1', 6)
        self.assertEqual('rating_between_1_and_5', str(context.exception))

    def test_rate_out_of_range3(self):
        self.client.checkout_book('zhangq1', '1')
        with self.assertRaises(Exception) as context:
            self.client.rate_book('zhangq1', '1', -1)
        self.assertEqual('rating_between_1_and_5', str(context.exception))

    def test_rate_twice(self):
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 1)
        self.client.rate_book('zhangq1', '1', 2)
        self.assertEqual(2, self.client.get_rating('zhangq1', '1'))

    def test_rate_borrower_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.rate_book('xx', '1', 1)
        self.assertEqual('borrower_not_exists', str(context.exception))

    def test_rate_book_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.rate_book('zhangq2', 'xxx', 1)
        self.assertEqual('book_not_exists', str(context.exception))
