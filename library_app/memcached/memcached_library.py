import json

import memcache

from library_app.model import Book, Borrower, Library

conn = memcache.Client(['127.0.0.1:11211'], debug=0)


def get_memcached():
    return conn


def book_to_str(book):
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
    return json.dumps(book_dict)


def str_to_book(dict):
    if not dict:
        return None
    dict = json.loads(dict)
    return Book(title=dict.get('title'), author=dict.get('author', []), isbn=dict.get('isbn'),
                page_num=dict.get('page_num'), quantity=dict.get('quantity'))


def borrower_to_str(borrower):
    if not borrower:
        return None
    borrower_dict = {}
    if borrower.username:
        borrower_dict['username'] = borrower.username
    if borrower.name:
        borrower_dict['name'] = borrower.name
    if borrower.phone:
        borrower_dict['phone'] = borrower.phone
    return json.dumps(borrower_dict)


def str_to_borrower(dict):
    if not dict:
        return None
    dict = json.loads(dict)
    return Borrower(username=dict.get('username'), name=dict.get('name'), phone=dict.get('phone'))


def set_hash(hash_key, entity, value):
    oldValue = get_memcached().hget(hash_key, entity)
    if oldValue:
        if not value:
            get_memcached().hdel(hash_key, entity)
        oldValue = str(oldValue, 'utf-8')
    if value:
        get_memcached().hset(hash_key, entity, value)
    return oldValue


def update_set_reference(refer_key, set_prefix, oldValue, newValue):
    if oldValue:
        get_memcached().add('-' + set_prefix + oldValue, '')
        get_memcached().append('-' + set_prefix + oldValue, refer_key)
    if newValue:
        get_memcached().add(set_prefix + newValue, '')
        get_memcached().append(set_prefix + newValue, refer_key)


class BookProxy:
    def __init__(self, isbn):
        self.book_key = 'book:' + str(isbn)
        self.book = str_to_book(get_memcached().get(self.book_key))

    @staticmethod
    def get_books(book_keys):
        return [str_to_book(get_memcached().get(key)) for key in book_keys]

    def add(self):
        get_memcached().add('book:keys', '')
        get_memcached().append('book:keys', ',' + self.book_key)

    def save(self):
        get_memcached().set(self.book_key, book_to_str(self.book))

    def exists(self):
        return self.book != None

    def edit(self, book, override):
        if not self.exists():
            self.book = Book(isbn=book.isbn)
        if override or book.title:
            self.set_title(book.title)
        if override or book.author:
            self.set_author(book.author)
        if override or book.page_num:
            self.set_page_num(book.page_num)
        if book.quantity:
            self.set_quantity(book.quantity)
        get_memcached().set(self.book_key, book_to_str(self.book))

    def delete(self):
        get_memcached().delete(self.book_key)
        get_memcached().srem('book:keys', self.book_key)
        self.set_title(None)
        self.set_author(None)
        self.set_page_num(None)
        get_memcached().delete(self.book_key)
        return False

    def set_title(self, title):
        oldValue = self.book.title if self.book else None
        self.book.title = title
        update_set_reference(self.book_key, 'book:title-', oldValue, title)

    def set_author(self, author):
        oldValue = None
        if self.book.author:
            oldValue = self.book.author
        self.book.author = author
        if oldValue:
            oldAuthors = oldValue.split(';')
            for oAuthor in oldAuthors:
                update_set_reference(self.book_key, 'book:author-', oAuthor, None)
        for nAuthor in author:
            update_set_reference(self.book_key, 'book:author-', None, nAuthor)

    def set_quantity(self, quantity):
        if not type(quantity) == int:
            raise Exception('quantity must be integer :' + str(quantity))
        self.book.quantity = quantity

    def get_quantity(self):
        self.fetch()
        return self.book.quantity

    def set_page_num(self, page_num):
        self.book.page_num = page_num

    def get_borrower_num(self):
        return get_memcached().scard('book:checkoutby-' + self.book_key)

    def is_borrower(self, borrowerProxy):
        return get_memcached().sismember('book:checkoutby-' + self.book_key, borrowerProxy.borrower_key)

    def add_borrower(self, borrowerProxy):
        get_memcached().sadd('book:checkoutby-' + self.book_key, borrowerProxy.borrower_key)
        get_memcached().sadd('borrower:checkoutby-' + borrowerProxy.borrower_key, self.book_key)

    def remove_borrower(self, borrowerProxy):
        get_memcached().srem('book:checkoutby-' + self.book_key, borrowerProxy.borrower_key)
        get_memcached().srem('borrower:checkoutby-' + borrowerProxy.borrower_key, self.book_key)


class BorrowerProxy:
    def __init__(self, username):
        self.username = username
        self.borrower_key = 'borrower:' + username
        self.borrower = str_to_borrower(get_memcached().get(self.borrower_key))

    def exists(self):
        return self.borrower != None

    def save(self):
        get_memcached().set(self.borrower_key, borrower_to_str(self.borrower))

    def edit(self, borrower):
        if not self.exists():
            self.borrower = Borrower(username=borrower.username)
        if borrower.name:
            self.set_name(borrower.name)
        if borrower.phone:
            self.set_phone(borrower.phone)
        self.save()

    def delete(self):
        self.set_name(None)
        self.set_phone(None)
        get_memcached().delete(self.borrower_key)

    def set_name(self, name):
        oldValue = self.borrower.name if self.borrower else None
        self.borrower.name = name
        update_set_reference(self.borrower_key, 'borrower:name-', oldValue, name)

    def set_phone(self, phone):
        self.borrower.phone = phone

    def get_borrowed_book_num(self):
        return get_memcached().scard('borrower:checkoutby-' + self.borrower_key)


class MemcachedLibrary(Library):
    def drop_db(self):
        get_memcached().flush_all()

    def add_book(self, book):
        Library.add_book(self, book)
        bookproxy = BookProxy(book.isbn)
        if bookproxy.exists():
            raise Exception('book_exist_already')
        bookproxy.add()
        bookproxy.edit(book, True)

    def get_book(self, isbn):
        return BookProxy(isbn).book

    def delete_book(self, isbn):
        proxy = BookProxy(isbn)
        if not proxy.exists():
            raise Exception('book_not_exists')
        if proxy.get_borrower_num() > 0:
            raise Exception('book_borrowed')
        proxy.delete()

    def edit_book(self, isbn, book, override=False):
        proxy = BookProxy(isbn)
        if not proxy.exists():
            raise Exception('book_not_exists')
        if book.quantity != None and book.quantity < proxy.get_borrower_num():
            raise Exception('book_borrowed')
        proxy.edit(book, override)

    def search_by_title(self, title):
        return BookProxy.get_books(get_memcached().smembers('book:title-' + title))

    def search_by_author(self, author):
        return BookProxy.get_books(get_memcached().smembers('book:author-' + author))

    def sort_by_title(self):  # return all books
        return BookProxy.get_books(get_memcached().sort('book:keys', by='*->title', alpha=True))

    def sort_by_author(self):  # return all books
        return BookProxy.get_books(get_memcached().sort('book:keys', by='*->author', alpha=True))

    def sort_by_isbn(self):  # return all books
        return BookProxy.get_books(get_memcached().sort('book:keys', alpha=True))

    def sort_by_page_num(self):  # return all books
        return BookProxy.get_books(get_memcached().sort('book:keys', by='*->page_num', alpha=True))

    def add_borrower(self, borrower):
        Library.add_borrower(self, borrower)
        proxy = BorrowerProxy(borrower.username)
        if proxy.exists():
            raise Exception('borrower_already_exists')
        proxy.edit(borrower)

    def get_borrower(self, username):
        return BorrowerProxy(username).borrower

    def delete_borrower(self, username):
        proxy = BorrowerProxy(username)
        if not proxy.exists():
            raise Exception('borrower_not_exists')
        if proxy.get_borrowed_book_num() > 0:
            raise Exception('book_borrowed')
        proxy.delete()

    def edit_borrower(self, username, borrower):
        proxy = BorrowerProxy(username)
        if not proxy.exists():
            raise Exception('borrower_not_exists')
        proxy.edit(borrower)

    def search_by_name(self, name):
        return BorrowerProxy.get_borrowers(get_memcached().smembers('borrower:name-' + name))

    def checkout_book(self, username, isbn):
        borrowerProxy = BorrowerProxy(username)
        if not borrowerProxy.exists():
            raise Exception('borrower_not_exists')
        proxy = BookProxy(isbn)
        if not proxy.exists():
            raise Exception('book_not_exists')
        # verify availability
        if proxy.is_borrower(borrowerProxy):
            raise Exception('book_already_borrowed')
        if proxy.get_borrower_num() >= proxy.get_quantity():
            raise Exception('book_not_available')
        proxy.add_borrower(borrowerProxy)

    def return_book(self, username, isbn):
        borrowerProxy = BorrowerProxy(username)
        if not borrowerProxy.exists():
            raise Exception('borrower_not_exists')
        proxy = BookProxy(isbn)
        if not proxy.exists():
            raise Exception('book_not_exists')
        # verify indeed borrowed
        if not proxy.is_borrower(borrowerProxy):
            raise Exception('book_not_borrowed')
        proxy.remove_borrower(borrowerProxy)

    def get_book_borrowers(self, isbn):
        proxy = BookProxy(isbn)
        if not proxy.exists():
            raise Exception('book_not_exists')
        return BorrowerProxy.get_borrowers(get_memcached().smembers('book:checkoutby-' + proxy.book_key))

    def get_borrowed_books(self, username):
        proxy = BorrowerProxy(username)
        if not proxy.exists():
            raise Exception('borrower_not_exists')
        return BookProxy.get_books(get_memcached().smembers('borrower:checkoutby-' + proxy.borrower_key))
