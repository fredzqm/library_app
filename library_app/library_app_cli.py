import click

from .config import Config
from .redis.library import RedisLibrary
from .model import Book, Borrower


config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option('--backend', '-b', is_flag=True, required=True, help='Specify the backend of this library')
@click.pass_context
@config
def cli(config, backend):
    config.client = RedisLibrary()

@cli.command()
@config
def drop_db(config):
    config.client.drop_db()
    click.echo('The database {0} is dropped', type(config.client))


@cli.command()
@click.option('--title', '-b', default=None, help='The title of the book')
@click.option('--author', '-a', default=None, help='The author of the book')
@click.option('--isbn', '-i', default=None, help='The isbn of the book')
@click.option('--page-num', '-p', default=None, type=click.INT, help='The page number of the book')
@config
def add_book(config, title, author, isbn, page_num):
    book = Book(title=title, author=author, isbn=isbn, page_num=page_num)
    config.client.add_book(book)
    click.echo('Created a book with id {0} : {1}'.format(book.id, str(book)))

@cli.command()
@click.argument('id', required=True)
@config
def get_book(config, id):
    book = config.client.get_book(id)
    click.echo('The book with id {0} : {1}'.format(id, str(book)))

@cli.command()
@click.argument('id', required=True)
@config
def delete_book(config, id):
    config.client.delete_book(id)
    click.echo('The book with id {0} is deleted'.format(id))

@cli.command()
@click.argument('id', required=True)
@click.option('--title', '-b', default=None, help='The title of the book')
@click.option('--author', '-a', default=None, help='The author of the book')
@click.option('--isbn', '-i', default=None, help='The isbn of the book')
@click.option('--page-num', '-p', default=None, type=click.INT, help='The page number of the book')
@config
def edit_book(config, id, title, author, isbn, page_num):
    book = Book(title=title, author=author, isbn=isbn, page_num=page_num)
    config.client.edit_book(id, book)
    click.echo('Updated the book with id {0} to {1}'.format(book.id, str(book)))

@cli.command()
@click.option('--title', '-b', default=None, help='The title of the book')
@config
def search_by_title(config, title):
    books = config.client.search_by_title(title)
    click.echo('found books with title {0} : {1}'.format(title, str(books)))

@cli.command()
@click.option('--author', '-a', default=None, help='The author of the book')
@config
def search_by_author(config, author):
    books = config.client.search_by_author(author)
    click.echo('found books with author {0} : {1}'.format(author, str(books)))

@cli.command()
@click.option('--isbn', '-i', default=None, help='The isbn of the book')
@config
def search_by_isbn(config, isbn):
    books = config.client.search_by_isbn(isbn)
    click.echo('found books with isbn {0} : {1}'.format(isbn, str(books)))

@cli.command()
@config
def sort_by_title(config):
    books = config.client.sort_by_title()
    click.echo('Books sorted by title: {0}'.format(str(books)))

@cli.command()
@config
def sort_by_author(config):
    books = config.client.sort_by_author()
    click.echo('Books sorted by author: {0}'.format(str(books)))

@cli.command()
@config
def sort_by_isbn(config):
    books = config.client.sort_by_isbn()
    click.echo('Books sorted by isbn: {0}'.format(str(books)))

@cli.command()
@config
def sort_by_page_num(config):
    books = config.client.sort_by_page_num()
    click.echo('Books sorted by page_num: {0}'.format(str(books)))

@cli.command()
@click.argument('username', required=True)
@click.option('--name', '-n', required=True, help='The name of the borrower')
@click.option('--phone', '-p', help='The phone number of the borrower')
@config
def add_borrower(config, username, name, phone):
    borrower = Borrower(username=username, name=name, phone=phone)
    config.client.add_borrower(borrower)
    click.echo('The borrower created: {0}'.format(borrower))

@cli.command()
@click.argument('username', required=True)
@config
def get_borrower(config, username):
    borrower = config.client.get_borrower(username)
    click.echo('The borrower found: {0}'.format(borrower))

@cli.command()
@click.argument('username', required=True)
@config
def delete_borrower(config, username):
    config.client.delete_borrower(username)
    click.echo('The borrower with username={0} is deleted'.format(username))

@cli.command()
@click.argument('username', required=True)
@click.option('--name', '-n', required=True, help='The name of the borrower')
@click.option('--phone', '-p', help='The phone number of the borrower')
@config
def edit_borrower(config, username, name, phone):
    borrower = Borrower(username=username, name=name, phone=phone)
    config.client.edit_borrower(username, borrower)
    click.echo('The borrower with username={0} is deleted'.format(username))


@cli.command()
@click.option('--name', '-n', required=True, help='The name of the borrower')
@config
def search_by_name(config, name):
    borrowers = config.client.search_by_name(name)
    click.echo('The borrowers with name {0} found : {1}'.format(name, str(borrowers)))

@cli.command()
@click.argument('username', required=True)
@click.argument('id', required=True)
@config
def checkout_book(config, username, id):
    config.client.checkout_book(username, id)
    click.echo('The borrowers with username={0} checkout out book with id={1}'.format(username, id))

@cli.command()
@click.argument('username', required=True)
@click.argument('id', required=True)
@config
def return_book(config, username, id):
    config.client.return_book(username, id)
    click.echo('The borrowers with username={0} returned book with id={1}'.format(username, id))

@cli.command()
@click.argument('username', required=True)
@config
def get_book_checkedoutby(config, username):
    books = config.client.get_book_checkedoutby(username)
    click.echo('The borrowers with username={0} has checkout {1}'.format(username, str(books)))

@cli.command()
@click.argument('id', required=True)
@config
def get_borrower_has(config, id):
    borrower = config.client.get_borrower_has(id)
    click.echo('The borrower {0} has checkout book with id={1}'.format(str(borrower), id))
