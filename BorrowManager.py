import sqlite3
from collections import namedtuple
from datetime import datetime, timedelta


class BorrowManager:

    def __init__(self, database):
        self.database = database
        self.cursor = None
        self.library = None
        self.all_books = None
        self.available_books = None
        self.borrowed_books = None
        self.borrows = None

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
            (book_id, borrower_id, current_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'))
        )

        print(
            f'Ksiazka {book_title} o ID: {book_id} '
            'zostala wypozyczona osobie o danych: '
            f'{borrower_name}, {borrower_email}'
        )

    def get_borrows(self):
        self.borrows = []

        self.cursor.execute(
            'SELECT borrowed_books.borrow_id, borrowed_books.book_id, '
            'books.title, borrowers.name, borrowers.email, '
            'borrowed_books.borrow_date, borrowed_books.return_date '
            'FROM borrowed_books '
            'JOIN borrowers ON borrowed_books.borrower_id = borrowers.id '
            'JOIN books ON borrowed_books.book_id = books.id;'
        )

        for borrow in self.cursor.fetchall():
            Borrow = namedtuple(
                'Borrow',
                [
                    'borrow_id',
                    'book_id',
                    'book_title',
                    'borrower_name',
                    'borrower_email',
                    'borrow_date',
                    'return_date'
                ])
            self.borrows.append(Borrow(*borrow))

        return self.borrows

    def rentals_after_deadline(self):
        rentals_after_deadline = []

        current_date = datetime.now()
        loans = self.get_borrows()    # Rozwiazanie chwilowe, napisz osobne zapytanie do bazy

        for borrower in loans:
            if borrower.return_date < current_date.strftime('%Y-%m-%d'):
                rentals_after_deadline.append(borrower)

        return rentals_after_deadline

    def return_book(self, borrow_id):
        # ta metoda skasuje status wypożyczenia, historia wypożyczeń zostaje zapamiętana:
        pass


# happy testing
with BorrowManager('baza.db') as pozycz:
    pozycz.borrow_book(13, 'Leon', 'adres e-mail')  # Uzupełnić i skasować przed poleceniem commit

with BorrowManager('baza.db') as baza:
    after_date = baza.rentals_after_deadline()
    print(after_date)
#
# with BorrowManager('baza.db') as pozycz:
#     ludzie = pozycz.get_borrows()
#     for x in ludzie:
#         print(x)
