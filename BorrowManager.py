import sqlite3
from collections import namedtuple
from datetime import datetime, timedelta


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


    def return_book(self, borrow_id):
        # ta metoda skasuje status wypożyczenia, historia wypożyczeń zostaje zapamiętana:
        pass


# happy testing
with BorrowManager('baza.db') as pozycz:
    borrowers = pozycz.get_borrowers()  # Uzupełnić i skasować przed poleceniem commit
    for borrower in borrowers:
        print(borrower)

