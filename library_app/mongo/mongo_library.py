from copy import copy

import pymongo
from bson.dbref import DBRef

from library_app.model import Book, Borrower, Library

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
    return Book(title=dict.get('title'), author=dict.get('author', []), isbn=dict.get('_id'),
                page_num=dict.get('page_num'), quantity=dict.get('quantity'))


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
        db.drop_collection('book')
        db.drop_collection('borrower')
        db.drop_collection('checkout')

    def add_book(self, book):
        Library.add_book(self, book)
        try:
            get_mongo_collection('book').insert_one(book_to_dict(book))
        except pymongo.errors.DuplicateKeyError as e:
            raise Exception('book_exist_already')

    def get_book(self, isbn):
        return dict_to_book(get_mongo_collection('book').find_one(isbn))

    def delete_book(self, isbn):
        checkout = get_mongo_collection('checkout').find_one({'book': DBRef('book', isbn)})
        if checkout:
            raise Exception('book_borrowed')
        result = get_mongo_collection('book').delete_one({'_id': isbn})
        if result.deleted_count == 0:
            raise Exception('book_not_exists')

    def edit_book(self, isbn, book, override=False):
        if not get_mongo_collection('book').find_one(isbn):
            raise Exception('book_not_exists')
        if book.quantity:
            cursor = get_mongo_collection('checkout').find({'book': DBRef('book', isbn)})
            if cursor.count() > book.quantity:
                raise Exception('book_borrowed')
        book = copy(book)
        book.isbn = None
        book_dict = book_to_dict(book)
        if override:
            if 'quantity' not in book_dict:
                book_dict['quantity'] = get_mongo_collection('book').find_one({'_id': isbn})['quantity']
            get_mongo_collection('book').find_one_and_replace({'_id': isbn}, book_dict)
        else:
            if len(book_dict) == 0:
                return
            get_mongo_collection('book').find_one_and_update({'_id': isbn}, {'$set': book_dict})

    def search_by_title(self, title):
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find({'title': title})]

    def search_by_author(self, author):
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find({'author': author})]

    def sort_by_title(self):
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find().sort('title')]

    def sort_by_author(self):
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find().sort('author')]

    def sort_by_isbn(self):
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find().sort('_id')]

    def sort_by_page_num(self):
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find().sort('page_num')]

    def add_borrower(self, borrower):
        Library.add_borrower(self, borrower)
        get_mongo_collection('borrower').insert_one(borrower_to_dict(borrower))

    def get_borrower(self, username):
        return dict_to_borrower(get_mongo_collection('borrower').find_one(username))

    def delete_borrower(self, username):
        if get_mongo_collection('checkout').find_one({'borrower': DBRef('borrower', username)}):
            raise Exception('book_borrowed')
        result = get_mongo_collection('borrower').delete_one({'_id': username})
        if result.deleted_count == 0:
            raise Exception('borrower_not_exists')

    def edit_borrower(self, username, borrower):
        if not get_mongo_collection('borrower').find_one(username):
            raise Exception('borrower_not_exists')
        borrower = copy(borrower)
        borrower.username = None
        borrower_dict = borrower_to_dict(borrower)
        if len(borrower_dict) == 0:
            return
        get_mongo_collection('borrower').find_one_and_update({'_id': username}, {'$set': borrower_dict})

    def search_by_name(self, name):
        return [dict_to_borrower(dict) for dict in get_mongo_collection('borrower').find({'name': name})]

    def checkout_book(self, username, isbn):
        book = get_mongo_collection('book').find_one(isbn)
        if not book:
            raise Exception('book_not_exists')
        if not get_mongo_collection('borrower').find_one(username):
            raise Exception('borrower_not_exists')
        if get_mongo_collection('checkout').find_one(
                {'book': DBRef('book', isbn), 'borrower': DBRef('borrower', username)}):
            raise Exception('book_already_borrowed')
        cursor = get_mongo_collection('checkout').find({'book': DBRef('book', isbn)})
        if cursor.count() == book['quantity']:
            raise Exception('book_not_available')
        get_mongo_collection('checkout').insert_one(
            {'borrower': DBRef('borrower', username), 'book': DBRef('book', isbn)})

    def return_book(self, username, isbn):
        if not get_mongo_collection('book').find_one(isbn):
            raise Exception('book_not_exists')
        if not get_mongo_collection('borrower').find_one(username):
            raise Exception('borrower_not_exists')
        if not get_mongo_collection('checkout').find_one(
                {'book': DBRef('book', isbn), 'borrower': DBRef('borrower', username)}):
            raise Exception('book_not_borrowed')
        get_mongo_collection('checkout').delete_one(
            {'borrower': DBRef('borrower', username), 'book': DBRef('book', isbn)})

    def get_book_borrowers(self, isbn):
        if not get_mongo_collection('book').find_one(isbn):
            raise Exception('book_not_exists')
        ls = [checkout['borrower'].id for checkout in
              get_mongo_collection('checkout').find({'book': DBRef('book', isbn)})]
        return [dict_to_borrower(dict) for dict in get_mongo_collection('borrower').find({'_id': {'$in': ls}})]

    def get_borrowed_books(self, username):
        if not get_mongo_collection('borrower').find_one(username):
            raise Exception('borrower_not_exists')
        ls = [checkout['book'].id for checkout in
              get_mongo_collection('checkout').find({'borrower': DBRef('borrower', username)})]
        return [dict_to_book(dict) for dict in get_mongo_collection('book').find({'_id': {'$in': ls}})]
