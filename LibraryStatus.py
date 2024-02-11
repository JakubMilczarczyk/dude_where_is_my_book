import sqlite3
from collections import namedtuple


class LibraryStatus:

    def __init__(self, database_name):
        self.database = database_name
        self.cursor = None
        self.connection = None
        self.all_books = None
        self.available_books = None
        self.borrowed_books = None
        self.borrowers = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(exc_val, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()

    def get_all_books(self):
        self.cursor.execute(
            'SELECT books.id, books.title, books.author, books.created_at '
            'FROM books;'
        )

        self.all_books = []

        for book in self.cursor.fetchall():
            Book = namedtuple(
                'Book',
                [
                    'book_id',
                    'title',
                    'author',
                    'created_at'
                ])
            self.all_books.append(Book(*book))

        return self.all_books

    def get_available_books(self):
        self.cursor.execute(
            'SELECT books.id, books.title, books.author, books.created_at '
            'FROM books '
            'LEFT JOIN borrowed_books ON books.id = borrowed_books.book_id '
            'WHERE borrowed_books.book_id IS NULL;'
        )

        self.available_books = []

        for book in self.cursor.fetchall():
            Book = namedtuple(
                'Book',
                [
                    'book_id',
                    'title',
                    'author',
                    'created_at'
                ])
            self.available_books.append(Book(*book))

        return self.available_books

    def get_borrowed_books(self):
        self.cursor.execute(
            'SELECT borrowed_books.borrow_id, borrowed_books.book_id, '
            'books.title, borrowers.name, '
            'borrowed_books.borrow_date, borrowed_books.return_date '
            'FROM borrowed_books '
            'JOIN borrowers ON borrowed_books.borrower_id = borrowers.id '
            'JOIN books ON borrowed_books.book_id = books.id;'
        )

        self.borrowed_books = []

        for borrow in self.cursor.fetchall():
            Borrow = namedtuple(
                'Borrow',
                [
                    'borrow_id',
                    'book_id',
                    'book_title',
                    'borrower_name',
                    'borrow_date',
                    'return_date'
            ])
            self.borrowed_books.append(Borrow(*borrow))

        return self.borrowed_books


# happy testing
with LibraryStatus('baza.db') as ksiazki:
    dostepne = ksiazki.get_all_books()
    for pozycja in dostepne:
        print(pozycja)

with LibraryStatus('baza.db') as ksiazki:
    pozyczone = ksiazki.get_borrowed_books()
    print(pozyczone)
