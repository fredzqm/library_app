import unittest

from library_app.library_test import LibraryTest, book_toadd, book_toadd2, book_toadd3, browser_toadd1,  browser_toadd2,  browser_toadd3,  browser_toadd4
from library_app.model import Book
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

    def test_rate_not_checked_out(self):
        with self.assertRaises(Exception) as context:
            self.client.rate_book('zhangq1', '1', 1)
        self.assertEqual('book_not_checked_out', str(context.exception))

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

    def test_recommend1(self):
        self.client.add_book(book_toadd2)
        self.client.add_borrower(browser_toadd2)
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 3)
        self.client.checkout_book('zhangq2', '1')
        self.client.rate_book('zhangq2', '1', 3)
        self.client.checkout_book('zhangq2', '2')
        self.client.rate_book('zhangq2', '2', 5)

        recommends = self.client.recommend('zhangq1')
        self.assertCountEqual([book_toadd2], recommends)

    def test_recommend_different_rating(self):
        self.client.add_book(book_toadd2)
        self.client.add_borrower(browser_toadd2)
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 3)
        self.client.checkout_book('zhangq2', '1')
        self.client.rate_book('zhangq2', '1', 4)
        self.client.checkout_book('zhangq2', '2')
        self.client.rate_book('zhangq2', '2', 5)

        recommends = self.client.recommend('zhangq1')
        self.assertCountEqual([], recommends)

    def test_recommend_below_4(self):
        self.client.add_book(book_toadd2)
        self.client.add_borrower(browser_toadd2)
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 3)
        self.client.checkout_book('zhangq2', '1')
        self.client.rate_book('zhangq2', '1', 3)
        self.client.checkout_book('zhangq2', '2')
        self.client.rate_book('zhangq2', '2', 3)

        recommends = self.client.recommend('zhangq1')
        self.assertCountEqual([], recommends)

    def test_recommend_already_checkout(self):
        self.client.add_book(book_toadd2)
        self.client.add_borrower(browser_toadd2)
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 3)
        self.client.checkout_book('zhangq2', '1')
        self.client.rate_book('zhangq2', '1', 3)
        self.client.checkout_book('zhangq2', '2')
        self.client.rate_book('zhangq2', '2', 5)
        self.client.checkout_book('zhangq1', '2')

        recommends = self.client.recommend('zhangq1')
        self.assertCountEqual([], recommends)

    def test_recommend_multiple_book(self):
        self.client.add_book(book_toadd2)
        self.client.add_book(book_toadd3)
        self.client.add_borrower(browser_toadd2)
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 3)
        self.client.checkout_book('zhangq2', '1')
        self.client.rate_book('zhangq2', '1', 3)
        self.client.checkout_book('zhangq2', '2')
        self.client.rate_book('zhangq2', '2', 5)
        self.client.checkout_book('zhangq2', '3')
        self.client.rate_book('zhangq2', '3', 4)

        recommends = self.client.recommend('zhangq1')
        self.assertCountEqual([book_toadd2, book_toadd3], recommends)

    def test_recommend_multiple_recomender(self):
        self.client.add_book(book_toadd2)
        self.client.add_borrower(browser_toadd2)
        self.client.add_borrower(browser_toadd3)
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 3)
        self.client.checkout_book('zhangq2', '1')
        self.client.rate_book('zhangq2', '1', 3)
        self.client.checkout_book('zhangq3', '1')
        self.client.rate_book('zhangq3', '1', 3)
        self.client.checkout_book('zhangq2', '2')
        self.client.rate_book('zhangq2', '2', 5)
        self.client.checkout_book('zhangq3', '2')
        self.client.rate_book('zhangq3', '2', 4)

        recommends = self.client.recommend('zhangq1')
        self.assertCountEqual([book_toadd2], recommends)

    def test_recommend_multiple_recomenders_recommend_multiple_book(self):
        self.client.edit_book("1", Book(quantity=10))
        self.client.add_book(book_toadd2)
        self.client.add_book(book_toadd3)
        self.client.add_borrower(browser_toadd2)
        self.client.add_borrower(browser_toadd3)
        self.client.add_borrower(browser_toadd4)
        self.client.checkout_book('zhangq1', '1')
        self.client.rate_book('zhangq1', '1', 3)
        self.client.checkout_book('zhangq2', '1')
        self.client.rate_book('zhangq2', '1', 3)
        self.client.checkout_book('zhangq3', '1')
        self.client.rate_book('zhangq3', '1', 3)

        self.client.checkout_book('zhangq2', '2')
        self.client.rate_book('zhangq2', '2', 5)
        self.client.checkout_book('zhangq4', '1')
        self.client.rate_book('zhangq4', '1', 3)

        self.client.checkout_book('zhangq3', '2')
        self.client.rate_book('zhangq3', '2', 4)
        self.client.checkout_book('zhangq3', '3')
        self.client.rate_book('zhangq3', '3', 5)

        recommends = self.client.recommend('zhangq1')
        self.assertCountEqual([book_toadd2, book_toadd3], recommends)

