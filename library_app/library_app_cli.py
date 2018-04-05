import click

from .config import Config
from .redis.redis_library import RedisLibrary
from .model import Book, Borrower

config = click.make_pass_decorator(Config, ensure=True)


def _list_str(books):
    return '\n\t' + '\n\t'.join(map(lambda b: str(b), books))


@click.group()
@click.option('--backend', '-b', default='redis', help='Specify the backend of this library')
@click.pass_context
@config
def cli(config, backend):
    if backend == 'redis':
        config.client = RedisLibrary()


@cli.command()
@config
def drop_db(config):
    '''
        Clean the database to start test from fresh

    '''
    config.client.drop_db()
    click.echo('The database {} is dropped'.format(str(type(config.client))))


@cli.command()
@click.argument('isbn', required=True)
@click.option('--title', '-t', required=True, help='The title of the book')
@click.option('--author', '-a', required=True, multiple=True, help='The author of the book')
@click.option('--page-num', '-p', required=True, type=click.INT, help='The page number of the book')
@click.option('--quantity', '-q', default=1, type=click.INT, help='The quantity of the book')
@config
def add_book(config, isbn, title, author, page_num, quantity=1):
    '''
        Add a book new book

    '''
    book = Book(isbn=isbn, title=title, author=author, page_num=page_num, quantity=quantity)
    config.client.add_book(book)
    click.echo('Created {} book with isbn={}: {}'.format(book.quantity, book.isbn, _list_str([book])))


@cli.command()
@click.argument('isbn', required=True)
@config
def get_book(config, isbn):
    '''
        Get a book by isbn id

    '''
    book = config.client.get_book(isbn)
    if book:
        click.echo('There are {} books with isbn={}: {}'.format(book.quantity, isbn, _list_str([book])))
    else:
        click.echo('There is no book with isbn={}'.format(book.quantity, isbn))


@cli.command()
@click.argument('isbn', required=True)
@config
def delete_book(config, isbn):
    '''
        Delete a book with isbn id

    '''
    try:
        config.client.delete_book(isbn)
        click.echo('The book with isbn={} is deleted'.format(isbn))
    except Exception as e:
        click.echo('The book with isbn={} cannot be deleted due to {}'.format(isbn, e))


@cli.command()
@click.argument('isbn', required=True)
@click.option('--title', '-b', default=None, help='The title of the book')
@click.option('--author', '-a', multiple=True, help='The author of the book')
@click.option('--isbn', '-i', default=None, help='The isbn of the book')
@click.option('--page-num', '-p', default=None, type=click.INT, help='The page number of the book')
@click.option('--quantity', '-q', default=1, type=click.INT, help='The quantity of the book')
@config
def edit_book(config, isbn, title, author, page_num, quantity):
    '''
        Edit a book with isbn id

    '''
    if len(author) == 0:
        author = None
    book = Book(title=title, author=author, isbn=isbn, page_num=page_num, quantity=quantity)
    try:
        config.client.edit_book(isbn, book)
        click.echo('Updated the book with isbn={} to {}'.format(book.isbn, _list_str([config.client.get_book(isbn)])))
    except Exception as e:
        click.echo('Cannot edit book with isbn={} due to {}'.format(isbn, e))


@cli.command()
@click.argument('title')
@config
def search_by_title(config, title):
    '''
        Find a book by title

    '''
    books = config.client.search_by_title(title)
    click.echo('Found books with title={} : {}'.format(title, _list_str(books)))


@cli.command()
@click.argument('author')
@config
def search_by_author(config, author):
    '''
        Find a book by Author

    '''
    books = config.client.search_by_author(author)
    click.echo('Found books with author={} : {}'.format(author, _list_str(books)))


@cli.command()
@config
def sort_by_title(config):
    '''
        Sort all books by title

    '''
    books = config.client.sort_by_title()
    click.echo('Books sorted by title: {}'.format(_list_str(books)))


@cli.command()
@config
def sort_by_author(config):
    '''
        Sort all books by author

    '''
    books = config.client.sort_by_author()
    click.echo('Books sorted by author: {}'.format(_list_str(books)))


@cli.command()
@config
def sort_by_isbn(config):
    '''
        Sort all books by isbn

    '''
    books = config.client.sort_by_isbn()
    click.echo('Books sorted by isbn: {}'.format(_list_str(books)))


@cli.command()
@config
def sort_by_page_num(config):
    '''
        Sort all books by page number

    '''
    books = config.client.sort_by_page_num()
    click.echo('Books sorted by page_num: {}'.format(_list_str(books)))


@cli.command()
@click.argument('username', required=True)
@click.option('--name', '-n', required=True, help='The name of the borrower')
@click.option('--phone', '-p', help='The phone number of the borrower')
@config
def add_borrower(config, username, name, phone):
    '''
        Add a borrower

    '''
    borrower = Borrower(username=username, name=name, phone=phone)
    try:
        config.client.add_borrower(borrower)
        click.echo('The borrower created: {}'.format(_list_str([borrower])))
    except Exception as e:
        click.echo('Cannot create borrower {} due to {}'.format(borrower, e))


@cli.command()
@click.argument('username', required=True)
@config
def get_borrower(config, username):
    '''
        Get a borrower by username

    '''
    borrower = config.client.get_borrower(username)
    click.echo('The borrower found: {}'.format(borrower))


@cli.command()
@click.argument('username', required=True)
@config
def delete_borrower(config, username):
    '''
        Delete a borrower

    '''
    config.client.delete_borrower(username)
    try:
        click.echo('The borrower with username={} is deleted'.format(username))
    except Exception as e:
        click.echo('Cannot delete the borrower with username={} due to '.format(username, e))


@cli.command()
@click.argument('username', required=True)
@click.option('--name', '-n', required=True, help='The name of the borrower')
@click.option('--phone', '-p', help='The phone number of the borrower')
@config
def edit_borrower(config, username, name, phone):
    '''
        Edit a borrower

    '''
    borrower = Borrower(username=username, name=name, phone=phone)
    try:
        config.client.edit_borrower(username, borrower)
        click.echo('The borrower with username={} is deleted'.format(config.client.get_borrower(username)))
    except Exception as e:
        click.echo('Cannot edit borrower due to {}'.format(username, e))


@cli.command()
@click.argument('name', required=True)
@config
def search_by_name(config, name):
    '''
        Search for borrowers by name

    '''
    borrowers = config.client.search_by_name(name)
    click.echo('The borrowers with name={} found : {}'.format(name, _list_str(borrowers)))


@cli.command()
@click.argument('username', required=True)
@click.argument('isbn', required=True)
@config
def checkout_book(config, username, isbn):
    '''
        A borrower check out a book

    '''
    try:
        config.client.checkout_book(username, isbn)
        click.echo('The borrower with username={} check outed out book with isbn={}'.format(username, isbn))
    except Exception as e:
        click.echo('Cannot check out book due to {}'.format(e))


@cli.command()
@click.argument('username', required=True)
@click.argument('isbn', required=True)
@config
def return_book(config, username, isbn):
    '''
        A borrower return a book

    '''
    try:
        config.client.return_book(username, isbn)
        click.echo('The borrowers with username={} returned book with isbn={}'.format(username, isbn))
    except Exception as e:
        click.echo('Cannot return book due to {}'.format(e))


@cli.command()
@click.argument('isbn', required=True)
@config
def get_book_borrowers(config, isbn):
    '''
        Get the borrowers that have borrowed this book

    '''

    borrowers = config.client.get_book_borrowers(isbn)
    if len(borrowers) == 0:
        click.echo('The book with isbn={} has not been checked out'.format(isbn))
    else:
        click.echo('The borrowers who has checked out book with isbn={}: {}'.format(isbn, _list_str(borrowers)))


@cli.command()
@click.argument('username', required=True)
@config
def get_borrowed_books(config, username):
    '''
        Get the books a borrower has borrowed

    '''

    books = config.client.get_borrowed_books(username)
    if len(books) == 0:
        click.echo('The user with username={} has not checked out any book'.format(username))
    else:
        click.echo('The user with username={} has checked out {}'.format(username, _list_str(books)))
