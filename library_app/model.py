class Book:
    def __init__(self, title=None, author=None, isbn=None, page_num=None, quantity=None):
        if page_num != None and type(page_num) != int:
            page_num = int(page_num)
        if quantity != None and type(quantity) != int:
            quantity = int(quantity)
        self.title = title
        self.author = author
        self.isbn = isbn
        self.page_num = page_num
        self.quantity = quantity

    def __repr__(self):
        return ('title: {0} author: {1} isbn: {2} page_num: {3}'.
            format(self.title, self.author, self.isbn, self.page_num))

    def __eq__(self, other):
        return (
            self.isbn == other.isbn and
            self.title == other.title and
            self.page_num == other.page_num)

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


# class Library:
#     def drop_db(self):
#         raise NotImplementedError()
#
#     def add_book(self, book):
#         raise NotImplementedError()
#
#     def get_book(self, book_id):
#         raise NotImplementedError()
#
#     def delete_book(self, book_id):
#         raise NotImplementedError()
#
#     def edit_book(self, book_id, book):
#         raise NotImplementedError()
#
#     def search_by_title(self, title):
#         raise NotImplementedError()
#
#     def search_by_author(self, author):
#         raise NotImplementedError()
#
#     def search_by_isbn(self, isbn):
#         raise NotImplementedError()
#
#     def sort_by_title(self): # return all books
#         raise NotImplementedError()
#
#     def sort_by_author(self): # return all books
#         raise NotImplementedError()
#
#     def sort_by_isbn(self): # return all books
#         raise NotImplementedError()
#
#     def sort_by_page_num(self): # return all books
#         raise NotImplementedError()
#
#     def add_borrower(self, borrower):
#         raise NotImplementedError()
#
#     def get_borrower(self, username):
#         raise NotImplementedError()
#
#     def delete_borrower(self, username):
#         raise NotImplementedError()
#
#     def edit_borrower(self, username, borrower):
#         raise NotImplementedError()
#
#     def search_by_name(self, name):
#         raise NotImplementedError()
#
#     def checkout_book(self, username, book_id):
#         raise NotImplementedError()
#
#     def return_book(self, username, book_id):
#         raise NotImplementedError()
#
#     def get_book_checkedoutby(self, checkoutby):
#         raise NotImplementedError()
#
#     def get_borrower_has(self, book_id):
#         raise NotImplementedError()
