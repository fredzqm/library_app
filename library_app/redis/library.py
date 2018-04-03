import redis
from library_app.model import Book, Borrower

conn = redis.Redis()

def get_redis():
    return conn

def parse_dict(dict, key):
    if key in dict:
        return str(dict.get(key), 'utf-8')
    return None

def set_hash_and_update_set_reference(hash_key, entity, set_prefix, value):
    v = get_redis().hget(hash_key, entity)
    if v:
        if not value:
            get_redis().hdel(hash_key, entity)
        get_redis().srem(set_prefix+str(v), hash_key)
    if value:
        get_redis().hset(hash_key, entity, value)
        get_redis().sadd(set_prefix+value, hash_key)

class BookProxy:
    def __init__(self, book_id):
        self.book_id = book_id
        self.book_key = 'book:'+str(book_id)

    @staticmethod
    def add():
        bookproxy = BookProxy(get_redis().incr('book:count'))
        get_redis().sadd('book:keys', bookproxy.book_key)
        return bookproxy

    @staticmethod
    def key_to_Book(key):
        dict = get_redis().hgetall(key)
        if type(key) != str:
            key = str(key, 'utf-8')
        if len(dict) == 0:
            return None
        return Book(id=key[6:],
            title=parse_dict(dict, b'title'),
            author=parse_dict(dict, b'author'),
            isbn=parse_dict(dict, b'isbn'),
            page_num=int(parse_dict(dict, b'page_num')),
            checkoutby=parse_dict(dict, b'checkoutby'))

    @staticmethod
    def getBooks(book_keys):
        return [BookProxy.key_to_Book(key) for key in book_keys]

    def fetch(self):
        return BookProxy.key_to_Book(self.book_key)
    
    def edit(self, book):
        if book.title:
            self.set_title(book.title)
        if book.author:
            self.set_author(book.author)
        if book.isbn:
            self.set_isbn(book.isbn)
        if book.page_num:
            self.set_page_num(book.page_num)
        if book.checkoutby:
            self.set_checkoutby(book.checkoutby)

    def delete(self):
        get_redis().delete(self.book_key)
        get_redis().srem('book:keys', self.book_key)
        self.set_title(None)
        self.set_author(None)
        self.set_isbn(None)
        self.set_page_num(None)
        self.set_checkoutby(None)

    def set_title(self, title):
        set_hash_and_update_set_reference(self.book_key, 'title', 'book:title-', title)

    def set_author(self, author):
        set_hash_and_update_set_reference(self.book_key, 'author', 'book:author-', author)

    def set_isbn(self, isbn):
        set_hash_and_update_set_reference(self.book_key, 'isbn', 'book:isbn-', isbn)

    def set_page_num(self, page_num):
        if page_num:
            get_redis().hset(self.book_key, 'page_num', page_num)

    def set_checkoutby(self, checkoutby):
        set_hash_and_update_set_reference(self.book_key, 'checkoutby', 'book:checkoutby-', checkoutby)


class BorrowerProxy:
    def __init__(self, username):
        self.username = username
        self.borrower_key = 'borrower:'+ username

    @staticmethod
    def key_to_borrower(key):
        dict = get_redis().hgetall(key)
        if len(dict) == 0:
            return None
        if type(key) != str:
            key = str(key, 'utf-8')
        return Borrower(username=key[9:],
                name=parse_dict(dict, b'name'),
                phone=parse_dict(dict, b'phone'))

    @staticmethod
    def get_borrowers(borrower_keys):
        return [BorrowerProxy.key_to_borrower(key) for key in borrower_keys]

    def fetch(self):
        return BorrowerProxy.key_to_borrower(self.borrower_key)
    
    def edit(self, borrower):
        if borrower.name:
            self.set_name(borrower.name)
        if borrower.phone:
            self.set_phone(borrower.phone)

    def delete(self):
        get_redis().delete(self.borrower_key)
        self.set_name(None)
        self.set_phone(None)

    def set_name(self, name):
        set_hash_and_update_set_reference(self.borrower_key, 'name', 'borrower:name-', name)

    def set_phone(self, phone):
        if phone:
            get_redis().hset(self.borrower_key, 'phone', phone)

class RedisLibrary:
    def drop_db(self):
        get_redis().flushall()

    def add_book(self, book):
        # book:count stored the largets book id that can exist
        bookproxy = BookProxy.add()
        bookproxy.edit(book)
        book.id = bookproxy.book_id

    def get_book(self, book_id):
        return BookProxy(book_id).fetch()

    def delete_book(self, book_id):
        BookProxy(book_id).delete()

    def edit_book(self, book_id, book):
        BookProxy(book_id).edit(book)

    def search_by_title(self, title):
        return BookProxy.getBooks(get_redis().smembers('book:title-'+title))

    def search_by_author(self, author):
        return BookProxy.getBooks(get_redis().smembers('book:author-'+author))

    def search_by_isbn(self, isbn):
        return BookProxy.getBooks(get_redis().smembers('book:isbn-'+isbn))

    def sort_by_title(self): # return all books
        return BookProxy.getBooks(get_redis().sort('book:keys', by='*->title', alpha=True))

    def sort_by_author(self): # return all books
        return BookProxy.getBooks(get_redis().sort('book:keys', by='*->author', alpha=True))

    def sort_by_isbn(self): # return all books
        return BookProxy.getBooks(get_redis().sort('book:keys', by='*->isbn', alpha=True))

    def sort_by_page_num(self): # return all books
        return BookProxy.getBooks(get_redis().sort('book:keys', by='*->page_num', alpha=True))

    def add_borrower(self, borrower):
        BorrowerProxy(borrower.username).edit(borrower)

    def get_borrower(self, username):
        return BorrowerProxy(username).fetch()

    def delete_borrower(self, username):
        BorrowerProxy(username).delete()

    def edit_borrower(self, username, borrower):
        BorrowerProxy(username).edit(borrower)

    def search_by_name(self, name):
        return BorrowerProxy.get_borrowers(get_redis().smembers('borrower:name-'+name))

    def checkout_book(self, username, book_id):
        BookProxy(book_id).set_checkoutby(username)

    def return_book(self, username, book_id):
        BookProxy(book_id).set_checkoutby(None)

    def get_book_checkedoutby(self, checkoutby):
        return BookProxy.getBooks(get_redis().smembers('book:checkoutby-'+checkoutby))

    def get_borrower_has(self, book_id):
        checkoutby = BookProxy(book_id).fetch().checkoutby
        if checkoutby:
            return BorrowerProxy(checkoutby).fetch()
        return None
