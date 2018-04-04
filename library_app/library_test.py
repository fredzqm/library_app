from .model import Book, Borrower
from copy import copy

book_toadd = Book(title='book title', author='Sriram', isbn='1', page_num=200, quantity=3)
book_toadd2 = Book(title='book small', author='Chandan', isbn='2', page_num=300)
book_toadd3 = Book(title='book small', author='Chandan', isbn='3', page_num=300)
browser_toadd1 = Borrower(username='zhangq1', name='Fred', phone='111')
browser_toadd2 = Borrower(username='zhangq2', name='Fred', phone='112')
browser_toadd3 = Borrower(username='zhangq3', name='Daniel', phone='113')
browser_toadd4 = Borrower(username='zhangq4', name='David', phone='114')


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
        self.client.drop_db()
        self.client.add_book(book_toadd)
        self.client.add_borrower(browser_toadd1)

    def test_init_data(self):
        book = self.client.get_book('1')
        broswer = self.client.get_borrower('zhangq1')

        self.assertEqual(book, book_toadd)
        self.assertEqual(broswer, browser_toadd1)

    def test_add_multiple_identical_book(self):
        self.client.add_book(book_toadd)
        self.assertTupleEqual(self.client.add_book(book_toadd), (False, 'book_exist_already'))

    def test_create_book_invalid_page_num(self):
        self.assertRaises(Exception, lambda: Book(page_num='one'))

    def test_create_book_int_str_page_num(self):
        Book(page_num='1')
        Book(page_num='10')

    def test_delete_book(self):
        self.assertTrue(self.client.delete_book('1'))

        self.assertEqual(self.client.get_book('1'), None)

    def test_delete_book_not_exist(self):
        self.assertFalse(self.client.delete_book('10'))

        self.assertEqual(self.client.get_book('10'), None)

    def test_edit_book(self):
        self.client.edit_book('1', Book(title='new book title'))

        book_toadd_edited = copy(book_toadd)
        book_toadd_edited.title = 'new book title'
        self.assertEqual(self.client.get_book('1'), book_toadd_edited)

    def test_edit_and_delete_book(self):
        self.client.add_book(book_toadd)
        self.client.edit_book('1', Book(title='new book title'))
        self.client.delete_book('2')

        book_toadd_edited = copy(book_toadd)
        book_toadd_edited.title = 'new book title'
        self.assertEqual(self.client.get_book('1'), book_toadd_edited)

    def test_edit_book_not_exist(self):
        self.assertFalse(self.client.edit_book('10', Book()))

    def test_search_byTitle(self):
        books = self.client.search_by_title(book_toadd.title)

        self.assertListEqual(books, [book_toadd])

    def test_search_by_title_after_edit(self):
        self.client.add_book(book_toadd2)
        self.client.edit_book('2', Book(title=book_toadd.title))
        books = self.client.search_by_title(book_toadd.title)

        edited_book_toadd_2 = copy(book_toadd2)
        edited_book_toadd_2.title = book_toadd.title
        self.assertCountEqual(books, [book_toadd, edited_book_toadd_2])

    def test_search_by_author(self):
        books = self.client.search_by_author(book_toadd.author)

        self.assertListEqual(books, [book_toadd])

    def test_search_by_isbn(self):
        books = self.client.search_by_isbn(book_toadd.isbn)

        self.assertListEqual(books, [book_toadd])

    def test_search_by_isbn_no_match(self):
        books = self.client.search_by_isbn('no_such_isbn')

        self.assertListEqual(books, [])

    def test_sort_by_isbn_no_match(self):
        self.client.add_book(book_toadd2)
        books = self.client.sort_by_isbn()

        self.assertListEqual(books, [book_toadd, book_toadd2])

    def test_sort_by_title(self):
        self.client.add_book(book_toadd2)
        books = self.client.sort_by_title()

        self.assertListEqual(books, [book_toadd2, book_toadd])

    def test_sort_by_title_after_delete(self):
        self.client.add_book(book_toadd2)
        self.client.delete_book('1')
        books = self.client.sort_by_title()

        self.assertListEqual(books, [book_toadd2])

    def test_sort_by_page_num(self):
        self.client.add_book(book_toadd2)
        books = self.client.sort_by_page_num()

        self.assertListEqual(books, [book_toadd, book_toadd2])

    def test_sort_by_page_num(self):
        self.client.add_book(book_toadd2)
        books = self.client.sort_by_page_num()

        self.assertListEqual(books, [book_toadd, book_toadd2])

    def test_delete_borrower(self):
        self.assertTrue(self.client.delete_borrower('zhangq1'))
        broswer = self.client.get_borrower('zhangq1')

        self.assertEqual(broswer, None)

    def test_delete_borrower_not_exist(self):
        self.assertFalse(self.client.delete_borrower('no_one'))

    def test_edit_browser(self):
        self.assertTrue(self.client.edit_borrower('zhangq1', Borrower(phone='300')))
        broswer = self.client.get_borrower('zhangq1')
        browser_edited = copy(browser_toadd1)
        browser_edited.phone = '300'
        self.assertEqual(broswer, browser_edited)

    def test_edit_borrower_not_exist(self):
        self.assertFalse(self.client.edit_borrower('no_one', Borrower()))

    def test_search_by_name(self):
        broswers = self.client.search_by_name('Fred')

        self.assertListEqual(broswers, [browser_toadd1])

    def test_search_byName(self):
        broswers = self.client.search_by_name('Fred')

        self.assertListEqual(broswers, [browser_toadd1])

    def test_search_by_name_after_add(self):
        self.client.add_borrower(browser_toadd2)
        broswers = self.client.search_by_name('Fred')

        self.assertCountEqual(broswers, [browser_toadd1, browser_toadd2])

    def test_checkout_book(self):
        self.client.checkout_book('zhangq1', '1')
        broswers = self.client.get_book_borrowers('1')
        self.assertEqual(broswers, [browser_toadd1])

        books_checkedout = self.client.get_borrowed_books('zhangq1')

        self.assertListEqual(books_checkedout, [book_toadd])

    def test_checkout_book_browser_not_exist(self):
        self.assertTupleEqual(self.client.checkout_book('xxx', '1'), (False, 'browser_not_exist'))

    def test_checkout_book_not_exist(self):
        self.assertTupleEqual(self.client.checkout_book('zhangq1', '4'), (False, 'book_not_exist'))

    def test_checkout_book_same_book(self):
        self.client.add_borrower(browser_toadd2)
        self.client.add_borrower(browser_toadd3)
        self.client.add_borrower(browser_toadd4)

        self.assertTrue(self.client.checkout_book('zhangq1', '1'))
        self.assertTrue(self.client.checkout_book('zhangq2', '1'))
        self.assertTrue(self.client.checkout_book('zhangq3', '1'))
        self.assertTupleEqual(self.client.checkout_book('zhangq4', '1'), (False, 'book_not_available'))

    def test_checkout_book_same_book_twice(self):
        self.client.add_borrower(browser_toadd3)

        self.assertTrue(self.client.checkout_book('zhangq1', '1'))
        self.assertTupleEqual(self.client.checkout_book('zhangq1', '1'), (False, 'book_already_borrowed'))

    def test_checkout_book_multiple(self):
        self.client.add_book(book_toadd2)
        self.assertTrue(self.client.checkout_book('zhangq1', '1'))
        self.assertTrue(self.client.checkout_book('zhangq1', '2'))

        broswer = self.client.get_book_borrowers('1')
        self.assertEqual(broswer, [browser_toadd1])
        broswer = self.client.get_book_borrowers('2')
        self.assertEqual(broswer, [browser_toadd1])

        books_checkedout = self.client.get_borrowed_books('zhangq1')
        self.assertCountEqual(books_checkedout, [book_toadd, book_toadd2])

    def test_return_book(self):
        self.assertTrue(self.client.checkout_book('zhangq1', '1'))
        self.assertTrue(self.client.return_book('zhangq1', '1'))

        self.assertListEqual(self.client.get_book_borrowers('1'), [])

        books_checkedout = self.client.get_borrowed_books('zhangq1')
        self.assertListEqual(books_checkedout, [])

    def test_return_book_not_checkedout(self):
        self.assertTupleEqual(self.client.return_book('zhangq1', '1'), (False, 'book_not_borrowed'))

    def test_return_book_browser_not_exist(self):
        self.assertTupleEqual(self.client.return_book('xxx', '1'), (False, 'browser_not_exist'))

    def test_return_book_not_exist(self):
        self.assertTupleEqual(self.client.return_book('zhangq1', '4'), (False, 'book_not_exist'))

    def test_return_book_not_checkedout(self):
        self.assertTupleEqual(self.client.return_book('zhangq1', '1'), (False, 'book_not_borrowed'))

    def test_get_book_borrowers_book_not_exist000(self):
        self.assertTupleEqual(self.client.get_book_borrowers('non_exist_book'), (None, 'book_not_exist'))
