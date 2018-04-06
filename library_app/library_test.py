from copy import copy

from .model import Book, Borrower

book_toadd = Book(title='book small', author=['Sriram'], isbn='1', page_num=200, quantity=3)
book_toadd2 = Book(title='book medium', author=['Chandan'], isbn='2', page_num=300, quantity=2)
book_toadd3 = Book(title='book big', author=['Chandan', 'Sriram'], isbn='3', page_num=300, quantity=1)
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

    def test_add_book_none_isbn(self):
        with self.assertRaises(Exception) as context:
            self.client.add_book(None)
        self.assertEqual('required_field_book.isbn', str(context.exception))
        with self.assertRaises(Exception) as context:
            self.client.add_book(Book())
        self.assertEqual('required_field_book.isbn', str(context.exception))

    def test_add_multiple_identical_book(self):
        with self.assertRaises(Exception) as context:
            self.client.add_book(book_toadd)
        self.assertEqual('book_exist_already', str(context.exception))

    def test_add_book_invalid_page_num(self):
        self.assertRaises(Exception, lambda: Book(page_num='one'))

    def test_add_book_invalid_page_num(self):
        with self.assertRaises(Exception) as context:
            self.client.add_book(Book(isbn='10', page_num='xx'))

        with self.assertRaises(Exception) as context:
            self.client.add_book(Book(isbn='10', page_num=None))
        self.assertEqual('required_posivitive_field_book.page_num', str(context.exception))
        with self.assertRaises(Exception) as context:
            self.client.add_book(Book(isbn='10', page_num=0))
        self.assertEqual('required_posivitive_field_book.page_num', str(context.exception))
        with self.assertRaises(Exception) as context:
            self.client.add_book(Book(isbn='10', page_num=-1))
        self.assertEqual('required_posivitive_field_book.page_num', str(context.exception))

    def test_add_book_invalid_quantity(self):
        with self.assertRaises(Exception) as context:
            self.client.add_book(Book(isbn='10', page_num=1, quantity='xxx'))

        with self.assertRaises(Exception) as context:
            self.client.add_book(Book(isbn='10', page_num=1, quantity=-1))
        self.assertEqual('posivitive_field_book.quantity', str(context.exception))
        with self.assertRaises(Exception) as context:
            self.client.add_book(Book(isbn='10', page_num=1, quantity=0))
        self.assertEqual('posivitive_field_book.quantity', str(context.exception))

    def test_add_book_default_quantity_1(self):
        book_with_no_quantity = Book(isbn='default', page_num=1, quantity=None)
        self.client.add_book(book_with_no_quantity)
        book_with_with_default_quantity = copy(book_with_no_quantity)
        book_with_with_default_quantity.quantity = 1

        book = self.client.get_book('default')
        self.assertEqual(book, book_with_with_default_quantity)

    def test_add_borrower_none_username(self):
        with self.assertRaises(Exception) as context:
            self.client.add_borrower(None)
        self.assertEqual('required_field_borrower.username', str(context.exception))
        with self.assertRaises(Exception) as context:
            self.client.add_borrower(Borrower())
        self.assertEqual('required_field_borrower.username', str(context.exception))

    def test_create_book(self):
        Book(page_num='1', quantity=2)
        Book(page_num=10, quantity='3')

    def test_delete_book(self):
        self.client.delete_book('1')

        self.assertEqual(self.client.get_book('1'), None)

    def test_delete_book_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.delete_book('10')
        self.assertEqual('book_not_exists', str(context.exception))

        self.assertEqual(self.client.get_book('10'), None)

    def test_delete_book_borrowed(self):
        self.client.checkout_book('zhangq1', '1')

        with self.assertRaises(Exception) as context:
            self.client.delete_book('1')
        self.assertEqual('book_borrowed', str(context.exception))

    def test_delete_book_returned(self):
        self.client.checkout_book('zhangq1', '1')
        self.client.return_book('zhangq1', '1')

        self.client.delete_book('1')
        self.assertEqual(self.client.get_book('1'), None)

    def test_edit_book(self):
        self.client.edit_book('1', Book(title='new book title'))

        book_toadd_edited = copy(book_toadd)
        book_toadd_edited.title = 'new book title'
        self.assertEqual(self.client.get_book('1'), book_toadd_edited)

    def test_edit_and_delete_book(self):
        self.client.add_book(book_toadd2)
        self.client.edit_book('1', Book(title='new book title'))
        self.client.delete_book('2')

        book_toadd_edited = copy(book_toadd)
        book_toadd_edited.title = 'new book title'
        self.assertEqual(self.client.get_book('1'), book_toadd_edited)

    def test_edit_book_empty_edit(self):
        self.client.edit_book('1', Book())

    def test_edit_book_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.edit_book('10', Book())
        self.assertEqual('book_not_exists', str(context.exception))

    def test_edit_book_quantity_up(self):
        self.client.checkout_book('zhangq1', '1')
        self.client.edit_book('1', Book(quantity=10))

        book_toadd_edited = copy(book_toadd)
        book_toadd_edited.quantity = 10
        self.assertEqual(self.client.get_book('1'), book_toadd_edited)

    def test_edit_book_quantity_down(self):
        self.client.add_borrower(browser_toadd2)
        self.client.add_borrower(browser_toadd3)
        self.client.checkout_book('zhangq2', '1')
        self.client.checkout_book('zhangq3', '1')
        self.client.edit_book('1', Book(quantity=2))

        book_toadd_edited = copy(book_toadd)
        book_toadd_edited.quantity = 2
        self.assertEqual(self.client.get_book('1'), book_toadd_edited)

    def test_edit_book_quantity_down_insufficient(self):
        self.client.add_borrower(browser_toadd2)
        self.client.add_borrower(browser_toadd3)
        self.client.checkout_book('zhangq1', '1')
        self.client.checkout_book('zhangq2', '1')

        with self.assertRaises(Exception) as context:
            self.client.edit_book('1', Book(quantity=1))
        self.assertEqual('book_borrowed', str(context.exception))

    def test_search_by_title(self):
        books = self.client.search_by_title(book_toadd.title)

        self.assertListEqual(books, [book_toadd])

    def test_search_by_title_empty(self):
        books = self.client.search_by_title('???')

        self.assertListEqual(books, [])

    def test_search_by_title_after_edit(self):
        self.client.add_book(book_toadd2)
        self.client.edit_book('2', Book(title=book_toadd.title))
        books = self.client.search_by_title(book_toadd.title)

        edited_book_toadd_2 = copy(book_toadd2)
        edited_book_toadd_2.title = book_toadd.title
        self.assertCountEqual(books, [book_toadd, edited_book_toadd_2])

    def test_search_by_author(self):
        self.client.add_book(book_toadd2)
        self.client.add_book(book_toadd3)
        books = self.client.search_by_author(book_toadd.author[0])

        self.assertCountEqual(books, [book_toadd, book_toadd3])

    def test_search_by_author2(self):
        self.client.add_book(book_toadd2)
        self.client.add_book(book_toadd3)
        books = self.client.search_by_author(book_toadd2.author[0])

        self.assertCountEqual(books, [book_toadd2, book_toadd3])

    def test_search_by_author_empty(self):
        self.client.add_book(book_toadd2)
        self.client.add_book(book_toadd3)
        books = self.client.search_by_author('no one')

        self.assertCountEqual(books, [])

    def test_sort_by_isbn(self):
        self.client.add_book(book_toadd3)
        self.client.add_book(book_toadd2)
        books = self.client.sort_by_isbn()

        self.assertListEqual(books, [book_toadd, book_toadd2, book_toadd3])

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
        self.client.delete_borrower('zhangq1')
        broswer = self.client.get_borrower('zhangq1')

        self.assertEqual(broswer, None)

    def test_delete_borrower_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.delete_borrower('no_one')
        self.assertEqual('borrower_not_exists', str(context.exception))

    def test_delete_borrower_has_borrowed_book(self):
        self.client.checkout_book('zhangq1', '1')
        with self.assertRaises(Exception) as context:
            self.client.delete_borrower('zhangq1')
        self.assertEqual('book_borrowed', str(context.exception))

    def test_edit_browser(self):
        self.client.edit_borrower('zhangq1', Borrower(phone='300'))
        broswer = self.client.get_borrower('zhangq1')
        browser_edited = copy(browser_toadd1)
        browser_edited.phone = '300'
        self.assertEqual(broswer, browser_edited)

    def test_edit_borrower_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.edit_borrower('no_one', Borrower())
        self.assertEqual('borrower_not_exists', str(context.exception))

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
        self.assertListEqual(broswers, [browser_toadd1])

        books_checkedout = self.client.get_borrowed_books('zhangq1')

        self.assertListEqual(books_checkedout, [book_toadd])

    def test_checkout_book_borrower_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.checkout_book('xxx', '1')
        self.assertEqual('borrower_not_exists', str(context.exception))

    def test_checkout_book_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.add_book(book_toadd)
        self.assertEqual('book_exist_already', str(context.exception))
        with self.assertRaises(Exception) as context:
            self.client.checkout_book('zhangq1', '4')
        self.assertEqual('book_not_exists', str(context.exception))

    def test_checkout_book_not_available(self):
        self.client.add_borrower(browser_toadd2)
        self.client.add_borrower(browser_toadd3)
        self.client.add_borrower(browser_toadd4)

        self.client.checkout_book('zhangq1', '1')
        self.client.checkout_book('zhangq2', '1')
        self.client.checkout_book('zhangq3', '1')

        with self.assertRaises(Exception) as context:
            self.client.checkout_book('zhangq4', '1')
        self.assertEqual('book_not_available', str(context.exception))

        self.client.return_book('zhangq1', '1')
        self.client.checkout_book('zhangq4', '1')

    def test_checkout_book_no_available(self):
        self.client.add_borrower(browser_toadd2)
        self.client.edit_book('1', Book(quantity=1))
        self.client.checkout_book('zhangq1', '1')

        with self.assertRaises(Exception) as context:
            self.client.checkout_book('zhangq2', '1')
        self.assertEqual('book_not_available', str(context.exception))

        self.client.return_book('zhangq1', '1')
        self.client.checkout_book('zhangq2', '1')

    def test_checkout_book_same_book_twice(self):
        self.client.add_borrower(browser_toadd3)

        self.client.checkout_book('zhangq1', '1')

        with self.assertRaises(Exception) as context:
            self.client.checkout_book('zhangq1', '1')
        self.assertEqual('book_already_borrowed', str(context.exception))

    def test_checkout_book_multiple(self):
        self.client.add_book(book_toadd2)
        self.client.checkout_book('zhangq1', '1')
        self.client.checkout_book('zhangq1', '2')

        broswer = self.client.get_book_borrowers('1')
        self.assertEqual(broswer, [browser_toadd1])
        broswer = self.client.get_book_borrowers('2')
        self.assertEqual(broswer, [browser_toadd1])

        books_checkedout = self.client.get_borrowed_books('zhangq1')
        self.assertCountEqual(books_checkedout, [book_toadd, book_toadd2])

    def test_checkout_book_multiple_2(self):
        self.client.add_book(book_toadd2)
        self.client.add_borrower(browser_toadd2)
        self.client.checkout_book('zhangq1', '1')
        self.client.checkout_book('zhangq1', '2')
        self.client.checkout_book('zhangq2', '1')
        self.client.checkout_book('zhangq2', '2')

        broswer = self.client.get_book_borrowers('1')
        self.assertCountEqual(broswer, [browser_toadd1, browser_toadd2])
        broswer = self.client.get_book_borrowers('2')
        self.assertCountEqual(broswer, [browser_toadd1, browser_toadd2])

        books_checkedout = self.client.get_borrowed_books('zhangq1')
        self.assertCountEqual(books_checkedout, [book_toadd, book_toadd2])
        books_checkedout = self.client.get_borrowed_books('zhangq2')
        self.assertCountEqual(books_checkedout, [book_toadd, book_toadd2])

    def test_return_book(self):
        self.client.checkout_book('zhangq1', '1')
        self.client.return_book('zhangq1', '1')

        self.assertListEqual(self.client.get_book_borrowers('1'), [])

        books_checkedout = self.client.get_borrowed_books('zhangq1')
        self.assertListEqual(books_checkedout, [])

    def test_return_book_not_checkedout(self):
        with self.assertRaises(Exception) as context:
            self.client.return_book('zhangq1', '1')
        self.assertEqual('book_not_borrowed', str(context.exception))

    def test_return_book_borrower_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.return_book('xxx', '1')
        self.assertEqual('borrower_not_exists', str(context.exception))

    def test_return_book_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.return_book('zhangq1', '4')
        self.assertEqual('book_not_exists', str(context.exception))

    def test_return_book_not_checkedout(self):
        with self.assertRaises(Exception) as context:
            self.client.return_book('zhangq1', '1')
        self.assertEqual('book_not_borrowed', str(context.exception))

    def test_get_borrowed_books_borrower_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.get_borrowed_books('no_one')
        self.assertEqual('borrower_not_exists', str(context.exception))

    def test_get_book_borrowers_book_not_exists(self):
        with self.assertRaises(Exception) as context:
            self.client.get_book_borrowers('non_exist_book')
        self.assertEqual('book_not_exists', str(context.exception))
