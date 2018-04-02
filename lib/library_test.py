from lib.model import Book, Borrower
from copy import copy

book_toadd = Book(title='book title', author='Sriram', isbn='10000', page_num=200)
book_toadd2 = Book(title='book small', author='Chandan', isbn='20000', page_num=300)
browser_toadd = Borrower(username='zhangq2', name='Fred', phone='111')
browser_toadd2 = Borrower(username='zhangq3', name='Fred', phone='112')

class LibraryTest(object):

	'''
	   This method should be overriden by the specific implementation.
	   It should 
	   1. drop the databases
	   2. create the self.client
	   3. final call super(LibraryTest, self).setUp() to pupulate db with initial data
	'''
	def setUp(self):
		if self.setUpClient:
			self.setUpClient()
		self.client.add_book(book_toadd)
		self.client.add_borrower(browser_toadd)

	def testInitData(self):
		book = self.client.get_book('1')
		broswer = self.client.get_borrower('zhangq2')

		self.assertEqual(book, book_toadd)
		self.assertEqual(broswer, browser_toadd)

	def test_non_int_page_num(self):
		self.assertRaises(Exception, lambda: Borrower(page_num='one'))

	def testDeleteBook(self):
		self.client.delete_book(1)

		self.assertEqual(self.client.get_book('1'), None)

	def testEditBook(self):
		self.client.edit_book(1, Book(title='new book title'))
		
		book_toadd_edited = copy(book_toadd)
		book_toadd_edited.title = 'new book title'
		self.assertEqual(self.client.get_book('1'), book_toadd_edited)

	def testSearchByTitle(self):
		books = self.client.search_by_title(book_toadd.title)

		self.assertListEqual(books, [book_toadd])

	def test_search_by_title_after_edit(self):
		self.client.add_book(book_toadd2)
		self.client.edit_book('2', Book(title=book_toadd.title))
		books = self.client.search_by_title(book_toadd.title)

		edited_book_toadd_2 = copy(book_toadd2)
		edited_book_toadd_2.title = book_toadd.title
		self.assertCountEqual(books, [book_toadd, edited_book_toadd_2])

	def testSearchByAuthor(self):
		books = self.client.search_by_author(book_toadd.author)

		self.assertListEqual(books, [book_toadd])

	def testSearchByIsbn(self):
		books = self.client.search_by_isbn(book_toadd.isbn)

		self.assertListEqual(books, [book_toadd])

	def testSearchByIsbn(self):
		books = self.client.search_by_isbn(book_toadd.isbn)

		self.assertListEqual(books, [book_toadd])

	def testSortByIsbn(self):
		self.client.add_book(book_toadd2)
		books = self.client.sort_by_isbn()

		self.assertListEqual(books, [book_toadd, book_toadd2])

	def testSortByTitle(self):
		self.client.add_book(book_toadd2)
		books = self.client.sort_by_title()

		self.assertListEqual(books, [book_toadd2, book_toadd])

	def testSortByTitleAfterDelete(self):
		self.client.add_book(book_toadd2)
		self.client.delete_book('1')
		books = self.client.sort_by_title()

		self.assertListEqual(books, [book_toadd2])

	def testSortByPageNum(self):
		self.client.add_book(book_toadd2)
		books = self.client.sort_by_page_num()

		self.assertListEqual(books, [book_toadd, book_toadd2])

	def testSortByPageNum(self):
		self.client.add_book(book_toadd2)
		books = self.client.sort_by_page_num()

		self.assertListEqual(books, [book_toadd, book_toadd2])

	def test_delete_borrower(self):
		self.client.delete_borrower('zhangq2')
		broswer = self.client.get_borrower('zhangq2')

		self.assertEqual(broswer, None)

	def testEditBrowser(self):
		self.client.edit_borrower('zhangq2', Borrower(phone='300'))
		broswer = self.client.get_borrower('zhangq2')
		browser_edited = copy(browser_toadd)
		browser_edited.phone = '300'
		self.assertEqual(broswer, browser_edited)

	def testSearchByName(self):
		broswers = self.client.search_by_name('Fred')

		self.assertListEqual(broswers, [browser_toadd])

	def testSearchByName(self):
		broswers = self.client.search_by_name('Fred')

		self.assertListEqual(broswers, [browser_toadd])

	def testSearchByNameAfterAdd(self):
		self.client.add_borrower(browser_toadd2)
		broswers = self.client.search_by_name('Fred')

		self.assertCountEqual(broswers, [browser_toadd, browser_toadd2])

	def testCheckoutBook(self):
		self.client.checkout_book('zhangq2', '1')
		broswer = self.client.get_borrower_has('1')
		self.assertEqual(broswer, browser_toadd)

		books_checkedout = self.client.get_book_checkedoutby('zhangq2')

		book_toadd_checkout = copy(book_toadd)
		book_toadd_checkout.checkoutby = 'zhangq2'
		self.assertListEqual(books_checkedout, [book_toadd_checkout])

	def testCheckoutBook(self):
		self.client.checkout_book('zhangq2', '1')
		broswer = self.client.get_borrower_has('1')
		self.assertEqual(broswer, browser_toadd)

		books_checkedout = self.client.get_book_checkedoutby('zhangq2')

		book_toadd_checkout = copy(book_toadd)
		book_toadd_checkout.checkoutby = 'zhangq2'
		self.assertListEqual(books_checkedout, [book_toadd_checkout])
