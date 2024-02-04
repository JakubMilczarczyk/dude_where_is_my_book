import sqlite3
from collections import namedtuple
from datetime import datetime, timedelta


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
            book_id, title, author, created_at = book
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
            book_id, title, author, created_at = book
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
            borrow_id, book_id, book_title, borrower_name, borrow_date, return_date = borrow
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


class BorrowManager:

    def __init__(self, database_name):
        self.database = database_name
        self.cursor = None
        self.library = None
        self.all_books = None
        self.available_books = None
        self.borrowed_books = None
        self.borrowers = None

    def __enter__(self):
        self.library = sqlite3.connect(self.database)
        self.cursor = self.library.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.library.commit()
        self.library.close()

    def borrow_book(self, book_id, borrower_name, borrower_email):

        current_date = datetime.now()
        borrow_time = timedelta(days=30)
        return_date = current_date + borrow_time

        self.cursor.execute(
            'SELECT title FROM books WHERE id = ?;',
            (book_id,)
        )
        book_title = self.cursor.fetchone()

        self.cursor.execute(
            'SELECT id FROM borrowers WHERE name = ? AND email = ?;',
            (borrower_name, borrower_email)
            )
        borrower_row = self.cursor.fetchone()

        if borrower_row is None:
            self.cursor.execute(
                'INSERT INTO borrowers (name, email) VALUES (?, ?);',
                (borrower_name, borrower_email)
                )
            borrower_id = self.cursor.lastrowid
        else:
            borrower_id = borrower_row[0]

        self.cursor.execute(
            'INSERT INTO borrowed_books (book_id, borrower_id, borrow_date, return_date) VALUES (?, ?, ?, ?);',
            (book_id, borrower_id, current_date, return_date)
        )

        print(
            f'Ksiazka {book_title} o ID: {book_id}'
            'zostala wypozyczona osobie o danych:'
            f'{borrower_name}, {borrower_email}'
        )

    def get_borrowers(self):
        self.borrowers = []

        self.cursor.execute(
            'SELECT borrowed_books.borrow_id, borrowed_books.book_id, '
            'books.title, borrowers.name, borrowers.email, '
            'borrowed_books.borrow_date, borrowed_books.return_date '
            'FROM borrowed_books '
            'JOIN borrowers ON borrowed_books.borrower_id = borrowers.id '
            'JOIN books ON borrowed_books.book_id = books.id;'
        )

        for borrower in self.cursor.fetchall():
            borrow_id, book_id, book_title, borrower_name, borrower_email, borrow_date, return_date = borrower
            Borrower = namedtuple(
                'Borrower',
                [
                    'borrow_id',
                    'book_id',
                    'book_title',
                    'borrower_name',
                    'borrower_email',
                    'borrow_date',
                    'return_date'
                ])
            self.borrowers.append(Borrower(*borrower))

            return self.borrowers

    # ta metoda skasuje status wypożyczenia, historia wypożyczeń zostaje zapamiętana:
    def return_book(self, borrow_id):
        pass


with LibraryStatus('baza.db') as ksiazki:
    dostepne = ksiazki.get_all_books()
    for pozycja in dostepne:
        print(pozycja)

with BorrowManager('baza.db') as pozycz:
    borrowers = pozycz.get_borrowers()  # Uzupełnić i skasować przed poleceniem commit
    for borrower in borrowers:
        print(borrower)


# with LibraryStatus('baza.db') as ksiazki:
#     pozyczone = ksiazki.get_borrowed_books()
#     print(pozyczone)

