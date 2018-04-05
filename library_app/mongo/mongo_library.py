import redis
from library_app.model import Book, Borrower, Library


class MongoLibrary:
    def drop_db(self):
        '''
            Drop the whole database so we can start from scratch

        '''
        raise NotImplementedError()

    def add_book(self, book):
        '''

        :param book:
        :raise: 'required_field_book.isbn', 'required_posivitive_field_book.page_num', 'posivitive_field_book.quantity', 'book_exist_already'
        '''
        raise NotImplementedError()

    def get_book(self, isbn):
        '''

        :param book_id:
        :return: get the book by isbn
        '''
        raise NotImplementedError()

    def delete_book(self, isbn):
        '''

        :param isbn:
        :raise: 'book_not_exists', 'book_borrowed'
        '''
        raise NotImplementedError()

    def edit_book(self, isbn, book):
        '''

        :param isbn:
        :param book:
        :raise: 'book_not_exists', 'book_borrowed'
        '''
        raise NotImplementedError()

    def search_by_title(self, title):
        '''

        :param title:
        :return: all books with this title
        '''
        raise NotImplementedError()

    def search_by_author(self, author):
        '''

        :param author:
        :return: all books by this author
        '''
        raise NotImplementedError()

    def sort_by_title(self):
        '''

        :return: all books sorted by title
        '''
        raise NotImplementedError()

    def sort_by_author(self):
        '''

        :return: all books sorted by author
        '''
        raise NotImplementedError()

    def sort_by_isbn(self):
        '''

        :return: all books sorted by isbn
        '''
        raise NotImplementedError()

    def sort_by_page_num(self):
        '''

        :return: all books sorted by page number
        '''
        raise NotImplementedError()

    def add_borrower(self, borrower):
        '''

        :param borrower:
        :raise: 'required_field_borrower.username', 'borrower_already_exists'
        '''
        raise NotImplementedError()

    def get_borrower(self, username):
        '''

        :param username:
        :return: the borrower with this username
        '''
        raise NotImplementedError()

    def delete_borrower(self, username):
        '''

        :param username:
        :raise 'borrower_not_exists', 'book_borrowed'
        '''
        raise NotImplementedError()

    def edit_borrower(self, username, borrower):
        '''

        :param username:
        :param borrower:
        :raise 'borrower_not_exists
        '''
        raise NotImplementedError()

    def search_by_name(self, name):
        '''

        :param name:
        :return: borrowers with this name
        '''
        raise NotImplementedError()

    def checkout_book(self, username, book_id):
        '''

        :param username:
        :param book_id:
        :raise 'book_not_exists', 'book_already_borrowed', 'book_not_available'
        '''
        raise NotImplementedError()

    def return_book(self, username, book_id):
        '''

        :param username:
        :param book_id:
        :raise: `borrower_not_exists`, `book_not_exists`, `book_not_borrowed`
        '''
        raise NotImplementedError()

    def get_book_borrowers(self, isbn):
        '''

        :param isbn:
        :return: the borrowers that have borrowed this book
        :raise: 'book_not_exists'
        '''
        raise NotImplementedError()


    def get_borrowed_books(self, username):
        '''

        :param username:
        :return:
        :raise: 'borrower_not_exists'
        '''
        raise NotImplementedError()
