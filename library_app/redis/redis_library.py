from library_app.model import Book, Borrower, Library
import redis

conn = redis.Redis()


def get_redis():
    return conn


def parse_dict(dict, key):
    if key in dict:
        return str(dict.get(key), 'utf-8')
    return None


def set_hash(hash_key, entity, value):
    oldValue = get_redis().hget(hash_key, entity)
    if oldValue:
        if not value:
            get_redis().hdel(hash_key, entity)
        oldValue = str(oldValue, 'utf-8')
    if value:
        get_redis().hset(hash_key, entity, value)
    return oldValue

def update_set_reference(refer_key, set_prefix, oldValue, newValue):
    if oldValue and newValue:
        get_redis().smove(set_prefix + oldValue, set_prefix + newValue, refer_key)
    elif oldValue:
        get_redis().srem(set_prefix + oldValue, refer_key)
    elif newValue:
        get_redis().sadd(set_prefix + newValue, refer_key)

def set_hash_and_update_set_reference(hash_key, entity, set_prefix, value):
    oldValue = set_hash(hash_key, entity, value)
    update_set_reference(hash_key, set_prefix, oldValue, value)

class BookProxy:
    def __init__(self, isbn):
        self.book_key = 'book:' + str(isbn)

    @staticmethod
    def key_to_Book(key):
        dict = get_redis().hgetall(key)
        if type(key) != str:
            key = str(key, 'utf-8')
        if len(dict) == 0:
            return None
        commaSeparatedAuthor = parse_dict(dict, b'author')
        return Book(isbn=key[5:],
                    title=parse_dict(dict, b'title'),
                    author=commaSeparatedAuthor.split(';')  if commaSeparatedAuthor else [],
                    page_num=int(parse_dict(dict, b'page_num')),
                    quantity=int(parse_dict(dict, b'quantity')))

    @staticmethod
    def get_books(book_keys):
        return [BookProxy.key_to_Book(key) for key in book_keys]

    def add(self):
        get_redis().sadd('book:keys', self.book_key)

    def fetch(self):
        return BookProxy.key_to_Book(self.book_key)

    def exists(self):
        return self.book_key in get_redis()

    def edit(self, book):
        if book.title:
            self.set_title(book.title)
        if book.author:
            self.set_author(book.author)
        if book.page_num:
            self.set_page_num(book.page_num)
        if book.quantity:
            self.set_quantity(book.quantity)

    def delete(self):
        get_redis().delete(self.book_key)
        get_redis().srem('book:keys', self.book_key)
        self.set_title(None)
        self.set_author(None)
        self.set_page_num(None)
        get_redis().delete(self.book_key)
        return False

    def set_title(self, title):
        set_hash_and_update_set_reference(self.book_key, 'title', 'book:title-', title)

    def set_author(self, author):
        if not author:
            author = []

        oldValue = set_hash(self.book_key, 'author', ';'.join(author))
        if oldValue:
            oldAuthors = oldValue.split(';')
            for oAuthor in oldAuthors:
                update_set_reference(self.book_key, 'book:author-', oAuthor, None)
        for nAuthor in author:
            update_set_reference(self.book_key, 'book:author-', None, nAuthor)

    def set_quantity(self, quantity):
        if not type(quantity) == int:
            raise Exception('quantity must be integer :' + str(quantity))
        set_hash(self.book_key, 'quantity', quantity)

    def get_quantity(self):
        return int(get_redis().hget(self.book_key, 'quantity'))

    def set_page_num(self, page_num):
        set_hash(self.book_key, 'page_num', page_num)

    def get_borrower_num(self):
        return get_redis().scard('book:checkoutby-'+self.book_key)

    def is_borrower(self, borrowerProxy):
        return get_redis().sismember('book:checkoutby-'+self.book_key, borrowerProxy.borrower_key)

    def add_borrower(self, borrowerProxy):
        get_redis().sadd('book:checkoutby-'+self.book_key, borrowerProxy.borrower_key)
        get_redis().sadd('borrower:checkoutby-'+borrowerProxy.borrower_key, self.book_key)

    def remove_borrower(self, borrowerProxy):
        get_redis().srem('book:checkoutby-'+self.book_key, borrowerProxy.borrower_key)
        get_redis().srem('borrower:checkoutby-'+borrowerProxy.borrower_key, self.book_key)

class BorrowerProxy:
    def __init__(self, username):
        self.username = username
        self.borrower_key = 'borrower:' + username

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

    def exists(self):
        return self.borrower_key in get_redis()

    def fetch(self):
        return BorrowerProxy.key_to_borrower(self.borrower_key)

    def edit(self, borrower):
        if borrower.name:
            self.set_name(borrower.name)
        if borrower.phone:
            self.set_phone(borrower.phone)

    def delete(self):
        self.set_name(None)
        self.set_phone(None)
        get_redis().delete(self.borrower_key)

    def set_name(self, name):
        set_hash_and_update_set_reference(self.borrower_key, 'name', 'borrower:name-', name)

    def set_phone(self, phone):
        if phone:
            get_redis().hset(self.borrower_key, 'phone', phone)

    def get_borrowed_book_num(self):
        return get_redis().scard('borrower:checkoutby-'+self.borrower_key)

class RedisLibrary(Library):
    def drop_db(self):
        get_redis().flushall()

    def add_book(self, book):
        if book is None or not book.isbn:
            raise Exception('required_field_book.isbn')
        if book.page_num is None or type(book.page_num) is not int or book.page_num <= 0:
            raise Exception('required_posivitive_field_book.page_num')
        if book.author is None or type(book.author) is not list:
            raise Exception('required_list_field_book.author')
        if book.quantity is None:
            book.quantity = 1
        elif type(book.quantity) is not int or book.quantity <= 0:
            raise Exception('posivitive_field_book.quantity')
        bookproxy = BookProxy(book.isbn)
        if bookproxy.exists():
            raise Exception('book_exist_already')
        bookproxy.add()
        bookproxy.edit(book)

    def get_book(self, book_id):
        return BookProxy(book_id).fetch()

    def delete_book(self, isbn):
        proxy = BookProxy(isbn)
        if not proxy.exists():
            raise Exception('book_not_exists')
        if proxy.get_borrower_num() > 0:
            raise Exception('book_borrowed')
        proxy.delete()

    def edit_book(self, isbn, book):
        proxy = BookProxy(isbn)
        if not proxy.exists():
            raise Exception('book_not_exists')
        if book.quantity != None and book.quantity < proxy.get_borrower_num():
            raise Exception('book_borrowed')
        proxy.edit(book)

    def search_by_title(self, title):
        return BookProxy.get_books(get_redis().smembers('book:title-' + title))

    def search_by_author(self, author):
        return BookProxy.get_books(get_redis().smembers('book:author-' + author))

    def sort_by_title(self):  # return all books
        return BookProxy.get_books(get_redis().sort('book:keys', by='*->title', alpha=True))

    def sort_by_author(self):  # return all books
        return BookProxy.get_books(get_redis().sort('book:keys', by='*->author', alpha=True))

    def sort_by_isbn(self):  # return all books
        return BookProxy.get_books(get_redis().sort('book:keys', alpha=True))

    def sort_by_page_num(self):  # return all books
        return BookProxy.get_books(get_redis().sort('book:keys', by='*->page_num', alpha=True))

    def add_borrower(self, borrower):
        if borrower is None or not borrower.username:
            raise Exception('required_field_borrower.username')
        proxy = BorrowerProxy(borrower.username)
        if proxy.exists():
            raise Exception('borrower_already_exists')
        proxy.edit(borrower)

    def get_borrower(self, username):
        return BorrowerProxy(username).fetch()

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
        return BorrowerProxy.get_borrowers(get_redis().smembers('borrower:name-' + name))

    def checkout_book(self, username, book_id):
        borrowerProxy = BorrowerProxy(username)
        if not borrowerProxy.exists():
            raise Exception('borrower_not_exists')
        proxy = BookProxy(book_id)
        if not proxy.exists():
            raise Exception('book_not_exists')
        # verify availability
        if proxy.is_borrower(borrowerProxy):
            raise Exception('book_already_borrowed')
        if proxy.get_borrower_num() >= proxy.get_quantity():
            raise Exception('book_not_available')
        proxy.add_borrower(borrowerProxy)

    def return_book(self, username, book_id):
        borrowerProxy = BorrowerProxy(username)
        if not borrowerProxy.exists():
            raise Exception('borrower_not_exists')
        proxy = BookProxy(book_id)
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
        return BorrowerProxy.get_borrowers(get_redis().smembers('book:checkoutby-' + proxy.book_key))

    def get_borrowed_books(self, username):
        proxy = BorrowerProxy(username)
        if not proxy.exists():
            raise Exception('borrower_not_exists')
        return BookProxy.get_books(get_redis().smembers('borrower:checkoutby-' + proxy.borrower_key))

