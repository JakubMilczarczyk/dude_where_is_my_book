import sqlite3
from datetime import datetime, timedelta


def create_connection(baza):
    # nawiązuje połączenie z bazą książek
    with sqlite3.connect(baza) as connection:
        cursor = connection.cursor()

    return cursor


def get_books(cursor):
    cursor.execute('SELECT * FROM books')
# literuje się po wszystkich wierszach z bazy i zwracam tuple

    for book in cursor.fetchall():  # każdy wiersz jest tuplą
        book_id, title, author, created_at = book
        print(book)


# get_books(create_connection('baza.db'))

class LibraryStatus:  # kontext manager łączy się plikiem który damy w init, otwiera plik i go zamyka

    def __init__(self, database_name):
        self.database = database_name
        self.cursor = None
        self.library = None
        self.all_books = None
        self.available_books = None
        self.borrowed_books = None
        self.borrowers = None

    def __enter__(self):    # Łączy się z bazą danych (plikiem) i zwraca cursor do pisania zapytań w SQL lite
        self.library = sqlite3.connect(self.database)
        self.cursor = self.library.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.library.commit()
        self.library.close()

    def get_all_books(self):
        self.cursor.execute(
            'SELECT books.id, books.title, books.author, books.created_at '
            'FROM books;'
        )

        self.all_books = []

        for book in self.cursor.fetchall():
            book_id, title, author, created_at = book
            self.all_books.append({           # TODO zamienić na tuple nazwane?
                'id': book_id,
                'title': title,
                'author': author,
            })

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
            self.available_books.append({  # TODO zamienić na tuple nazwane?
                'id': book_id,
                'title': title,
                'author': author,
            })

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

        for book in self.cursor.fetchall():
            borrow_id, book_id, book_title, borrower_name, borrow_date, return_date = book
            self.borrowed_books.append({
                'borrow_id': borrow_id,
                'book_id': book_id,
                'tite': book_title,
                'name': borrower_name,
                'borrow_date': borrow_date,
                'return_date': return_date
            })

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

        self.cursor.execute('SELECT title FROM books WHERE id = ?;', (book_id,))
        book_title = self.cursor.fetchone()

        self.cursor.execute('SELECT id FROM borrowers WHERE name = ? AND email = ?;', (borrower_name, borrower_email))
        borrower_row = self.cursor.fetchone()

        if borrower_row is None:
            self.cursor.execute('INSERT INTO borrowers (name, email) VALUES (?, ?);', (borrower_name, borrower_email))
            borrower_id = self.cursor.lastrowid
        else:
            borrower_id = borrower_row[0]

        self.cursor.execute(
            'INSERT INTO borrowed_books (book_id, borrower_id, borrow_date, return_date) VALUES (?, ?, ?, ?);',
            (book_id, borrower_id, current_date, return_date)
        )

        print(
            f'Książka {book_title} o ID: {book_id}'
            'została wypożyczona osobie o danych:'
            f'{borrower_name}, {borrower_email}'
        )

    def return_book(self, borrow_id):   # kasuje status wypożyczenia, historia wypożyczeń zostaje zapamiętana
        return None


with LibraryStatus('baza.db') as ksiazki:
    dostępne = ksiazki.get_all_books()
    for pozycja in dostępne:
        print(pozycja)

with BorrowManager('baza.db') as pozycz:
    pozycz.borrow_book()  # Uzupełnić i skasować przed poleceniem commit

with LibraryStatus('baza.db') as ksiazki:
    pozyczone = ksiazki.get_borrowed_books()
    print(pozyczone)

