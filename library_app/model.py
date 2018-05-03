class Book:
    def __init__(self, title=None, author=[], isbn=None, page_num=None, quantity=None):
        if page_num is not None and type(page_num) != int:
            page_num = int(page_num)
        if quantity is not None and type(quantity) != int:
            quantity = int(quantity)
        self.title = title
        self.author = author
        self.isbn = isbn
        self.page_num = page_num
        self.quantity = quantity

    def __repr__(self):
        return ('isbn: {} title: {} author: {} page_num: {} quantity: {}'.
                format(self.isbn, self.title, self.author, self.page_num, self.quantity))

    def __eq__(self, other):
        return (
                self.isbn == other.isbn and
                self.title == other.title and
                self.author == other.author and
                self.page_num == other.page_num and
                self.quantity == other.quantity)

    def __hash__(self):
        return hash(str(self))


class Borrower:
    def __init__(self, username=None, name=None, phone=None):
        self.username = username
        self.name = name
        self.phone = phone

    def __repr__(self):
        return 'username: {} name: {} phone: {}'.format(self.username, self.name, self.phone)

    def __eq__(self, other):
        return (
                self.username == other.username and
                self.name == other.name and
                self.phone == other.phone)

    def __hash__(self):
        return hash(str(self))


class Library:
    def drop_db(self):
        '''
            Drop the whole database so we can start from scratch

        '''
        pass

    def add_book(self, book):
        '''

        :param book:
        :raise: 'required_field_book.isbn', 'required_posivitive_field_book.page_num', 'posivitive_field_book.quantity', 'book_exist_already'
        '''
        if book is None or not book.isbn:
            raise Exception('required_field_book.isbn')
        if book.page_num is None or type(book.page_num) is not int or book.page_num <= 0:
            raise Exception('required_posivitive_field_book.page_num')
        if book.author is None or (type(book.author) is not list and type(book.author) is not tuple):
            raise Exception('required_list_field_book.author')
        if book.quantity is None:
            book.quantity = 1
        elif type(book.quantity) is not int or book.quantity <= 0:
            raise Exception('posivitive_field_book.quantity')

    def get_book(self, isbn):
        '''

        :param isbn:
        :return: get the book by isbn
        '''
        pass

    def delete_book(self, isbn):
        '''

        :param isbn:
        :raise: 'book_not_exists', 'book_borrowed'
        '''
        pass

    def edit_book(self, isbn, book, override=False):
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
        if borrower is None or not borrower.username:
            raise Exception('required_field_borrower.username')

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

    def checkout_book(self, username, isbn):
        '''

        :param username:
        :param isbn:
        :raise 'book_not_exists', 'borrower_not_exists', 'book_already_borrowed', 'book_not_available'
        '''
        raise NotImplementedError()

    def return_book(self, username, isbn):
        '''

        :param username:
        :param isbn:
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

    def rate_book(self, username, isbn, rating):
        '''

        :param username:
        :param isbn:
        :param rating:
        :return:
        :raise: 'borrower_not_exists'
        :raise: 'book_not_exists'
        :raise: 'rating_between_1_and_5'
        :raise: 'book_not_checked_out'
        '''
        pass

    def get_rating(self, username, isbn):
        '''

        :param username:
        :param isbn:
        :return:
        :raise: 'borrower_not_exists'
        :raise: 'book_not_exists'
        :raise: 'book_not_checked_out'
        '''
        return 0

    def recommend(self, username):
        '''

        :param username:
        :raise: 'borrower_not_exists'
        :return:
        '''
        return []