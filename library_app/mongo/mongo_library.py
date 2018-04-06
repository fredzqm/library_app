from library_app.model import Book, Borrower, Library
from bson.dbref import DBRef
from copy import copy
import pymongo

client = pymongo.MongoClient()
db = client['library_db']

def get_mongo_collection(collection):
    return db[collection]

def book_to_dict(book):
    if not book:
        return None
    book_dict = {}
    if book.isbn:
        book_dict['_id'] = book.isbn
    if book.title:
        book_dict['title'] = book.title
    if book.author:
        book_dict['author'] = book.author
    if book.page_num:
        book_dict['page_num'] = book.page_num
    if book.quantity:
        book_dict['quantity'] = book.quantity
    return book_dict

def dict_to_book(dict):
    if not dict:
        return None
    return Book(title=dict.get('title'), author=dict.get('author', []), isbn=dict.get('_id'), page_num=dict.get('page_num'), quantity=dict.get('quantity'))

def borrower_to_dict(borrower):
    if not borrower:
        return None
    borrower_dict = {}
    if borrower.username:
        borrower_dict['_id'] = borrower.username
    if borrower.name:
        borrower_dict['name'] = borrower.name
    if borrower.phone:
        borrower_dict['phone'] = borrower.phone
    return borrower_dict

def dict_to_borrower(dict):
    if not dict:
        return None
    return Borrower(username=dict.get('_id'), name=dict.get('name'), phone=dict.get('phone'))


class MongoLibrary(Library):
    def drop_db(self):
        '''
            Drop the whole database so we can start from scratch

        '''
        db.drop_collection('book')
        db.drop_collection('borrower')
        db.drop_collection('checkout')

    def add_book(self, book):
        '''

        :param book:
        :raise: 'required_field_book.isbn', 'required_posivitive_field_book.page_num', 'posivitive_field_book.quantity', 'book_exist_already'
        '''
        Library.add_book(self, book)
        try:
            get_mongo_collection('book').insert_one(book_to_dict(book))
        except pymongo.errors.DuplicateKeyError as e:
            raise Exception('book_exist_already')

    def get_book(self, isbn):
        '''

        :param isbn:
        :return: get the book by isbn
        '''
        return dict_to_book(get_mongo_collection('book').find_one(isbn))

    def delete_book(self, isbn):
        '''

        :param isbn:
        :raise: 'book_not_exists', 'book_borrowed'
        '''
        # try:
        checkout = get_mongo_collection('checkout').find_one({'book': DBRef('book', isbn)})
        if checkout:
            raise Exception('book_borrowed')
        result = get_mongo_collection('book').delete_one({'_id': isbn})
        if result.deleted_count == 0:
            raise Exception('book_not_exists')

    def edit_book(self, isbn, book):
        '''

        :param isbn:
        :param book:
        :raise: 'book_not_exists', 'book_borrowed'
        '''
        # update = {}
        # if book.author:
        #     update['author'] = book.author
        # if book.page_num:
        #     update['page_num'] = book.page_num
        # if book.quantity:
        #     update['quantity'] = book.quantity
        if not get_mongo_collection('book').find_one(isbn):
            raise Exception('book_not_exists')
        if book.quantity:
            cursor = get_mongo_collection('checkout').find({'book': DBRef('book', isbn)})
            if cursor.count() > book.quantity:
                raise Exception('book_borrowed')
        book = copy(book)
        book.isbn = None
        book_dict = book_to_dict(book)
        if len(book_dict) == 0:
            return
        get_mongo_collection('book').find_one_and_update({'_id': isbn}, {'$set': book_dict})

    def search_by_title(self, title):
        '''

        :param title:
        :return: all books with this title
        '''
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find({'title': title})]

    def search_by_author(self, author):
        '''

        :param author:
        :return: all books by this author
        '''
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find({'author': author})]


    def sort_by_title(self):
        '''

        :return: all books sorted by title
        '''
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find().sort('title')]

    def sort_by_author(self):
        '''

        :return: all books sorted by author
        '''
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find().sort('author')]


    def sort_by_isbn(self):
        '''

        :return: all books sorted by isbn
        '''
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find().sort('_id')]


    def sort_by_page_num(self):
        '''

        :return: all books sorted by page number
        '''
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find().sort('page_num')]

    def add_borrower(self, borrower):
        '''

        :param borrower:
        :raise: 'required_field_borrower.username', 'borrower_already_exists'
        '''
        Library.add_borrower(self, borrower)
        get_mongo_collection('borrower').insert_one(borrower_to_dict(borrower))

    def get_borrower(self, username):
        '''

        :param username:
        :return: the borrower with this username
        '''
        return dict_to_borrower(get_mongo_collection('borrower').find_one(username))

    def delete_borrower(self, username):
        '''

        :param username:
        :raise 'borrower_not_exists', 'book_borrowed'
        '''
        result = get_mongo_collection('borrower').delete_one({'_id': username})
        if result.deleted_count == 0:
            raise Exception('borrower_not_exists')
        if get_mongo_collection('checkout').find_one({'borrower': DBRef('borrower', username)}):
            raise Exception('book_borrowed')

    def edit_borrower(self, username, borrower):
        '''

        :param username:
        :param borrower:
        :raise 'borrower_not_exists
        '''
        if not get_mongo_collection('borrower').find_one(username):
            raise Exception('borrower_not_exists')
        borrower = copy(borrower)
        borrower.username = None
        borrower_dict = borrower_to_dict(borrower)
        if len(borrower_dict) == 0:
            return
        get_mongo_collection('borrower').find_one_and_update({'_id': username}, {'$set': borrower_dict})

    def search_by_name(self, name):
        '''

        :param name:
        :return: borrowers with this name
        '''
        return [dict_to_borrower(dict) for dict in get_mongo_collection('borrower').find({'name': name})]

    def checkout_book(self, username, isbn):
        '''

        :param username:
        :param isbn:
        :raise 'book_not_exists', 'borrower_not_exists', 'book_already_borrowed', 'book_not_available'
        '''
        book = get_mongo_collection('book').find_one(isbn)
        if not book:
            raise Exception('book_not_exists')
        if not get_mongo_collection('borrower').find_one(username):
            raise Exception('borrower_not_exists')
        if get_mongo_collection('checkout').find_one({'book': DBRef('book', isbn), 'borrower': DBRef('borrower', username)}):
            raise Exception('book_already_borrowed')
        cursor = get_mongo_collection('checkout').find({'book': DBRef('book', isbn)})
        if cursor.count() == book['quantity']:
            raise Exception('book_not_available')
        get_mongo_collection('checkout').insert_one({'borrower': DBRef('borrower', username), 'book': DBRef('book', isbn)})

    def return_book(self, username, isbn):
        '''

        :param username:
        :param isbn:
        :raise: `borrower_not_exists`, `book_not_exists`, `book_not_borrowed`
        '''
        if not get_mongo_collection('book').find_one(isbn):
            raise Exception('book_not_exists')
        if not get_mongo_collection('borrower').find_one(username):
            raise Exception('borrower_not_exists')
        if not get_mongo_collection('checkout').find_one({'book': DBRef('book', isbn), 'borrower': DBRef('borrower', username)}):
            raise Exception('book_not_borrowed')
        get_mongo_collection('checkout').delete_one({'borrower': DBRef('borrower', username), 'book': DBRef('book', isbn)})


    def get_book_borrowers(self, isbn):
        '''

        :param isbn:
        :return: the borrowers that have borrowed this book
        :raise: 'book_not_exists'
        '''
        if not get_mongo_collection('book').find_one(isbn):
            raise Exception('book_not_exists')
        ls =  [checkout['borrower'].id for checkout in get_mongo_collection('checkout').find({'book': DBRef('book', isbn)})]
        return [dict_to_borrower(dict) for dict in get_mongo_collection('borrower').find({'_id': {'$in': ls}})]

    def get_borrowed_books(self, username):
        '''

        :param username:
        :return:
        :raise: 'borrower_not_exists'
        '''
        if not get_mongo_collection('borrower').find_one(username):
            raise Exception('borrower_not_exists')
        ls =  [checkout['book'].id for checkout in get_mongo_collection('checkout').find({'borrower': DBRef('borrower', username)})]
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find({'_id': {'$in': ls}})]
