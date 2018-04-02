import redis
from lib.library import Book, Browser

conn = redis.Redis()

def getRedis():
    return conn

def parseDict(dict, key):
    if key in dict:
        return str(dict.get(key), 'utf-8')
    return None

def setHashAndUpdateSetReference(hash_key, entity, set_prefix, value):
    v = getRedis().hget(hash_key, entity)
    if v:
        if not value:
            getRedis().hdel(hash_key, entity)
        getRedis().srem(set_prefix+str(v), hash_key)
    if value:
        getRedis().hset(hash_key, entity, value)
        getRedis().sadd(set_prefix+value, hash_key)

class BookProxy:
    def __init__(self, book_id):
        self.book_id = book_id
        self.book_key = 'book:'+str(book_id)

    @staticmethod
    def add():
        bookproxy = BookProxy(getRedis().incr('book:count'))
        getRedis().sadd('book:keys', bookproxy.book_key)
        return bookproxy

    @staticmethod
    def keyToBook(key):
        dict = getRedis().hgetall(key)
        if type(key) != str:
            key = str(key, 'utf-8')
        if len(dict) == 0:
            return None
        return Book(id=key[5:],
            title=parseDict(dict, b'title'),
            author=parseDict(dict, b'author'),
            isbn=parseDict(dict, b'isbn'),
            page_num=int(parseDict(dict, b'page_num')),
            checkoutby=parseDict(dict, b'checkoutby'))

    @staticmethod
    def getBooks(book_keys):
        return [BookProxy.keyToBook(key) for key in book_keys]

    def fetch(self):
        return BookProxy.keyToBook(self.book_key)
    
    def edit(self, book):
        if book.title:
            self.setTitle(book.title)
        if book.author:
            self.setAuthor(book.author)
        if book.isbn:
            self.setIsbn(book.isbn)
        if book.page_num:
            self.setPageNum(book.page_num)
        if book.checkoutby:
            self.setCheckoutby(book.checkoutby)

    def delete(self):
        getRedis().delete(self.book_key)
        getRedis().srem('book:keys', self.book_key)
        self.setTitle(None)
        self.setAuthor(None)
        self.setIsbn(None)
        self.setPageNum(None)
        self.setCheckoutby(None)

    def setTitle(self, title):
        setHashAndUpdateSetReference(self.book_key, 'title', 'book:title-', title)

    def setAuthor(self, author):
        setHashAndUpdateSetReference(self.book_key, 'author', 'book:author-', author)

    def setIsbn(self, isbn):
        setHashAndUpdateSetReference(self.book_key, 'isbn', 'book:isbn-', isbn)

    def setPageNum(self, page_num):
        if page_num:
            getRedis().hset(self.book_key, 'page_num', page_num)

    def setCheckoutby(self, checkoutby):
        setHashAndUpdateSetReference(self.book_key, 'checkoutby', 'book:checkoutby-', checkoutby)


class BrowserProxy:
    def __init__(self, username):
        self.username = username
        self.browser_key = 'browser:'+ username

    @staticmethod
    def keyToBrowser(key):
        dict = getRedis().hgetall(key)
        if len(dict) == 0:
            return None
        if type(key) != str:
            key = str(key, 'utf-8')
        return Browser(username=key[8:],
                name=parseDict(dict, b'name'),
                phone=parseDict(dict, b'phone'))

    @staticmethod
    def getBrowsers(browser_keys):
        return [BrowserProxy.keyToBrowser(key) for key in browser_keys]

    def fetch(self):
        return BrowserProxy.keyToBrowser(self.browser_key)
    
    def edit(self, browser):
        if browser.name:
            self.setName(browser.name)
        if browser.phone:
            self.setPhone(browser.phone)

    def delete(self):
        getRedis().delete(self.browser_key)
        self.setName(None)
        self.setPhone(None)

    def setName(self, name):
        setHashAndUpdateSetReference(self.browser_key, 'name', 'browser:name-', name)

    def setPhone(self, phone):
        if phone:
            getRedis().hset(self.browser_key, 'phone', phone)

class RedisLibrary:
    def addBook(self, book):
        # book:count stored the largets book id that can exist
        bookproxy = BookProxy.add()
        bookproxy.edit(book)
        book.id = bookproxy.book_id

    def getBook(self, book_id):
        return BookProxy(book_id).fetch()

    def deleteBook(self, book_id):
        BookProxy(book_id).delete()

    def editBook(self, book_id, book):
        BookProxy(book_id).edit(book)

    def searchByTitle(self, title):
        return BookProxy.getBooks(getRedis().smembers('book:title-'+title))

    def searchByAuthor(self, author):
        return BookProxy.getBooks(getRedis().smembers('book:author-'+author))

    def searchByIsbn(self, isbn):
        return BookProxy.getBooks(getRedis().smembers('book:isbn-'+isbn))

    def sortByTitle(self): # return all books
        return BookProxy.getBooks(getRedis().sort('book:keys', by='*->title', alpha=True))

    def sortByAuthor(self): # return all books
        return BookProxy.getBooks(getRedis().sort('book:keys', by='*->author', alpha=True))

    def sortByIsbn(self): # return all books
        return BookProxy.getBooks(getRedis().sort('book:keys', by='*->isbn', alpha=True))

    def sortByPageNum(self): # return all books
        return BookProxy.getBooks(getRedis().sort('book:keys', by='*->page_num', alpha=True))

    def addBrowser(self, browser):
        BrowserProxy(browser.username).edit(browser)

    def getBrowser(self, username):
        return BrowserProxy(username).fetch()

    def deleteBrowser(self, username):
        BrowserProxy(username).delete()

    def editBrowser(self, username, browser):
        BrowserProxy(username).edit(browser)

    def searchByName(self, name):
        return BrowserProxy.getBrowsers(getRedis().smembers('browser:name-'+name))

    def searchByUsername(self, username):
        return BrowserProxy(username).fetch()

    def checkoutBook(self, username, book_id):
        BookProxy(book_id).setCheckoutby(username)

    def returnBook(self, username, book_id):
        BookProxy(book_id).setCheckoutby(None)

    def getBookCheckedOutBy(self, checkoutby):
        bookIds = getRedis().smembers('book:checkoutby-'+checkoutby)
        return [BookProxy(id).fetch() for id in bookIds]

    def getBrowserHas(self, book_id):
        checkoutby = BookProxy(book_id).fetch().checkoutby
        if checkoutby:
            return BrowserProxy(checkoutby).fetch()
        return None
