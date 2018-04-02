
class Book:
    def __init__(self, id, title, author, isbn, page_num):
        self.id = id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.page_num = page_num

class Browser:
    def __init__(self, name, username, phone):
        self.name = name
        self.username = username
        self.phone = phone

class Library:
    def addBook(book):
        raise NotImplementedError();

    def deleteBook(book_id):
        raise NotImplementedError();

    def editBook(book_id, book):
        raise NotImplementedError();

    def searchByTitle(title):
        raise NotImplementedError();

    def searchByAuthor(author):
        raise NotImplementedError();

    def searchByIsbn(isbn):
        raise NotImplementedError();

    def addBrowser(browser):
        raise NotImplementedError();

    def deleteBrowser(browser_username):
        raise NotImplementedError();

    def editBrowser(username, browser):
        raise NotImplementedError();

    def searchByName(name):
        raise NotImplementedError();

    def searchByUsername(username):
        raise NotImplementedError();

    def checkoutBook(username, book_id):
        raise NotImplementedError()

    def returnBook(username, book_id):
        raise NotImplementedError()

    def getBookCheckedOutBy(username):
        raise NotImplementedError()

    def getUserHas(book_id):
        raise NotImplementedError()
