from neo4j.v1 import GraphDatabase

from library_app.model import Book, Borrower, Library

neo4jDriver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))
sess = neo4jDriver.session()


def book_to_dict(book):
    if not book:
        return None
    book_dict = {}
    if book.isbn:
        book_dict['isbn'] = book.isbn
    else:
        book_dict['isbn'] = None
    if book.title:
        book_dict['title'] = book.title
    else:
        book_dict['title'] = None
    if book.author:
        book_dict['author'] = book.author
    else:
        book_dict['author'] = None
    if book.page_num:
        book_dict['page_num'] = book.page_num
    else:
        book_dict['page_num'] = None
    if book.quantity:
        book_dict['quantity'] = book.quantity
    else:
        book_dict['quantity'] = None
    return book_dict


def dict_to_book(dict):
    if not dict:
        return None
    return Book(title=dict.get('title'), author=dict.get('author', []), isbn=dict.get('isbn'),
                page_num=dict.get('page_num'), quantity=dict.get('quantity'))


def borrower_to_dict(borrower):
    if not borrower:
        return None
    borrower_dict = {}
    if borrower.username:
        borrower_dict['username'] = borrower.username
    if borrower.name:
        borrower_dict['name'] = borrower.name
    if borrower.phone:
        borrower_dict['phone'] = borrower.phone
    return borrower_dict


def dict_to_borrower(dict):
    if not dict:
        return None
    return Borrower(username=dict.get('username'), name=dict.get('name'), phone=dict.get('phone'))


class Neo4jLibrary:
    def drop_db(self):
        '''
            Drop the whole database so we can start from scratch

        '''
        sess.run('MATCH (n) DETACH DELETE n')

    def add_book(self, book):
        '''

        :param book:
        :raise: 'required_field_book.isbn', 'required_posivitive_field_book.page_num', 'posivitive_field_book.quantity', 'book_exist_already'
        '''
        Library.add_book(self, book)
        if self.get_book(book.isbn) is not None:
            raise Exception('book_exist_already')
        sess.run("CREATE (:book {"
                 "title: {title},"
                 "isbn: {isbn},"
                 "author: {author},"
                 "page_num: {page_num},"
                 "quantity: {quantity}"
                 "})", book_to_dict(book))

    def get_book(self, isbn):
        '''

        :param isbn:
        :return: get the book by isbn
        '''
        for x in sess.run("MATCH (b:book)"
                          "WHERE b.isbn={isbn}"
                          "RETURN b", isbn=isbn):
            return dict_to_book(x['b'])
        return None

    def delete_book(self, isbn):
        '''

        :param isbn:
        :raise: 'book_not_exists', 'book_borrowed'
        '''
        if self.get_book(isbn) is None:
            raise Exception('book_not_exists')
        if self._get_checkout_count(isbn) > 0:
            raise Exception('book_borrowed')
        sess.run("MATCH (b:book)"
                 "WHERE b.isbn={isbn}"
                 "DELETE b", isbn=isbn)

    def edit_book(self, isbn, book, override=False):
        '''

        :param isbn:
        :param book:
        :raise: 'book_not_exists', 'book_borrowed'
        '''
        old_book = self.get_book(isbn)
        if old_book is None:
            raise Exception('book_not_exists')
        if override or book.title:
            old_book.title = book.title
        if override or book.author:
            old_book.author = book.author
        if override or book.page_num:
            old_book.page_num = book.page_num
        if book.quantity:
            old_book.quantity = book.quantity
            count = self._get_checkout_count(isbn)
            if count > book.quantity:
                raise Exception('book_borrowed')
        sess.run("MATCH (b:book)"
                 "WHERE b.isbn={isbn}"
                 "SET b.title={title},"
                 "b.author={author},"
                 "b.page_num={page_num},"
                 "b.quantity={quantity}"
                 , book_to_dict(old_book))

    def search_by_title(self, title):
        '''

        :param title:
        :return: all books with this title
        '''
        return [dict_to_book(x['b']) for x in sess.run("MATCH (b:book)"
                                                       "WHERE b.title={title}"
                                                       "RETURN b", title=title)]

    def search_by_author(self, author):
        '''

        :param author:
        :return: all books by this author
        '''
        return [dict_to_book(x['b']) for x in
                sess.run("MATCH (b:book)"
                         "WHERE {author} in b.author "
                         "RETURN b", author=author)]

    def sort_by_title(self):
        '''

        :return: all books sorted by title
        '''
        return [dict_to_book(x['b']) for x in
                sess.run("MATCH (b:book)"
                         "RETURN b "
                         "ORDER BY b.title")]

    def sort_by_author(self):
        '''

        :return: all books sorted by author
        '''
        return [dict_to_book(x['b']) for x in
                sess.run("MATCH (b:book)"
                         "RETURN b "
                         "ORDER BY b.author")]

    def sort_by_isbn(self):
        '''

        :return: all books sorted by isbn
        '''
        return [dict_to_book(x['b']) for x in
                sess.run("MATCH (b:book)"
                         "RETURN b "
                         "ORDER BY b.isbn")]

    def sort_by_page_num(self):
        '''

        :return: all books sorted by page number
        '''
        return [dict_to_book(x['b']) for x in
                sess.run("MATCH (b:book)"
                         "RETURN b "
                         "ORDER BY b.page_num")]

    def add_borrower(self, borrower):
        '''

        :param borrower:
        :raise: 'required_field_borrower.username', 'borrower_already_exists'
        '''
        Library.add_borrower(self, borrower)
        sess.run("CREATE (:borrower {"
                 "username: {username},"
                 "name: {name},"
                 "phone: {phone}"
                 "})", borrower_to_dict(borrower))

    def get_borrower(self, username):
        '''

        :param username:
        :return: the borrower with this username
        '''
        for x in sess.run("MATCH (b:borrower)"
                          "WHERE b.username={username}"
                          "RETURN b", username=username):
            return dict_to_borrower(x['b'])

    def delete_borrower(self, username):
        '''

        :param username:
        :raise 'borrower_not_exists', 'book_borrowed'
        '''
        if self.get_borrower(username) is None:
            raise Exception('borrower_not_exists')
        if self._get_borrowed_count(username) > 0:
            raise Exception('book_borrowed')
        sess.run("MATCH (b:borrower)"
                 "WHERE b.username={username}"
                 "DELETE b", username=username)

    def edit_borrower(self, username, borrower, override=False):
        '''

        :param username:
        :param borrower:
        :raise 'borrower_not_exists
        '''
        old_borrower = self.get_borrower(username)
        if old_borrower is None:
            raise Exception('borrower_not_exists')
        if override or borrower.name:
            old_borrower.name = borrower.name
        if override or borrower.phone:
            old_borrower.phone = borrower.phone
        sess.run("MATCH (b:borrower)"
                 "WHERE b.username={username}"
                 "SET b.name={name},"
                 "b.phone={phone}", borrower_to_dict(old_borrower))

    def search_by_name(self, name):
        '''

        :param name:
        :return: borrowers with this name
        '''
        return [dict_to_borrower(x['b']) for x in
                sess.run("MATCH (b:borrower)"
                         "WHERE b.name={name} "
                         "RETURN b", name=name)]

    def checkout_book(self, username, isbn):
        '''

        :param username:
        :param isbn:
        :raise 'book_not_exists', 'borrower_not_exists', 'book_already_borrowed', 'book_not_available'
        '''
        book = self.get_book(isbn)
        if not book:
            raise Exception('book_not_exists')
        if not self.get_borrower(username):
            raise Exception('borrower_not_exists')
        if self._has_borrowed_book(isbn, username):
            raise Exception('book_already_borrowed')
        count = self._get_checkout_count(isbn)
        if count == book.quantity:
            raise Exception('book_not_available')
        sess.run("MATCH (u:borrower), (b:book)"
                 "WHERE u.username={username} and b.isbn={isbn}"
                 "CREATE (u)-[:checkout]->(b)", username=username, isbn=isbn)

    def _has_borrowed_book(self, isbn, username):
        for x in sess.run("MATCH (u:borrower)-[c:checkout]->(b:book)"
                          "WHERE u.username={username} and b.isbn={isbn}"
                          "RETURN c", username=username, isbn=isbn):
            return True
        return False

    def _get_checkout_count(self, isbn):
        num_checkout_itr = iter(sess.run("MATCH (u:borrower)-[c:checkout]->(b:book)"
                                         "WHERE b.isbn={isbn}"
                                         "RETURN count(*)", isbn=isbn))
        count = next(num_checkout_itr)
        return count.value()

    def _get_borrowed_count(self, username):
        num_checkout_itr = iter(sess.run("MATCH (u:borrower)-[c:checkout]->(b:book)"
                                         "WHERE u.username={username}"
                                         "RETURN count(*)", username=username))
        count = next(num_checkout_itr)
        return count.value()

    def return_book(self, username, isbn):
        '''

        :param username:
        :param isbn:
        :raise: `borrower_not_exists`, `book_not_exists`, `book_not_borrowed`
        '''
        borrower = self.get_borrower(username)
        if not borrower:
            raise Exception('borrower_not_exists')
        book = self.get_book(isbn)
        if not book:
            raise Exception('book_not_exists')
        # verify indeed borrowed
        if not self._has_borrowed_book(isbn, username):
            raise Exception('book_not_borrowed')
        sess.run("MATCH (u:borrower)-[c:checkout]->(b:book)"
                 "WHERE u.username={username} and b.isbn={isbn}"
                 "DELETE c", username=username, isbn=isbn)

    def get_book_borrowers(self, isbn):
        '''

        :param isbn:
        :return: the borrowers that have borrowed this book
        :raise: 'book_not_exists'
        '''
        if self.get_book(isbn) is None:
            raise Exception('book_not_exists')
        return [dict_to_borrower(x['u']) for x in
                sess.run("MATCH (u:borrower)-[:checkout]->(b:book)"
                         "WHERE b.isbn={isbn} "
                         "RETURN u", isbn=isbn)]

    def get_borrowed_books(self, username):
        '''

        :param username:
        :return:
        :raise: 'borrower_not_exists'
        '''
        if self.get_borrower(username) is None:
            raise Exception('borrower_not_exists')
        return [dict_to_book(x['b']) for x in
                sess.run("MATCH (u:borrower)-[:checkout]->(b:book)"
                         "WHERE u.username={username} "
                         "RETURN b", username=username)]

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
        if rating < 1 or rating > 5:
            raise Exception('rating_between_1_and_5')
        if not self.get_book(isbn):
            raise Exception('book_not_exists')
        if not self.get_borrower(username):
            raise Exception('borrower_not_exists')
        if not self._has_borrowed_book(isbn, username):
            raise Exception('book_not_checked_out')
        sess.run("MATCH (u:borrower)-[c:checkout]->(b:book)"
                 "WHERE u.username={username} and b.isbn={isbn}"
                 "SET c.rating={rating}", username=username, isbn=isbn, rating=rating)

    def get_rating(self, username, isbn):
        '''

        :param username:
        :param isbn:
        :return:
        :raise: 'borrower_not_exists'
        :raise: 'book_not_exists'
        :raise: 'book_not_checked_out'
        '''
        if not self.get_book(isbn):
            raise Exception('book_not_exists')
        if not self.get_borrower(username):
            raise Exception('borrower_not_exists')
        if not self._has_borrowed_book(isbn, username):
            raise Exception('book_not_checked_out')
        for x in sess.run("MATCH (u:borrower)-[c:checkout]->(b:book)"
                          "WHERE u.username={username} and b.isbn={isbn}"
                          "return c.rating", username=username, isbn=isbn):
            return x['c.rating']
        return 0
