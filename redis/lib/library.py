import redis

class Book:
    def __init__(self, id=None, title=None, author=None, isbn=None, page_num=None, checkoutby=None):
        if page_num != None and type(page_num) != int:
            raise Exception('page number need to be an integer')
        self.id = id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.page_num = page_num
        self.checkoutby = checkoutby

    def __repr__(self):
        return ('title: {0} author: {1} isbn: {2} page_num: {3} checkoutby: {4}'.
            format(self.title, self.author, self.isbn, self.page_num, self.checkoutby))

    def __eq__(self, other):
        return (
            self.title == other.title and 
            self.isbn == other.isbn and 
            self.page_num == other.page_num and 
            self.checkoutby == other.checkoutby)

    def __hash__(self):
        return hash(str(self))

class Borrower:
    def __init__(self, username=None, name=None, phone=None):
        self.username = username
        self.name = name
        self.phone = phone    

    def __repr__(self):
        return 'username: {0} name: {1} phone: {2}'.format(self.username, self.name, self.phone)

    def __eq__(self, other):
        return (
            self.username == other.username and 
            self.name == other.name and 
            self.phone == other.phone)

    def __hash__(self):
        return hash(str(self))
