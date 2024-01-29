import sqlite3


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

class AccessibleBooks: # kontext manager łączy się plikiem który damy w init, otwiera plik i go zamyka

    def __init__(self, file_name):
        self.database = file_name
        self.cursor = None
        self.library = None
        self.books = None
        self.borrowers = None
        self.book_loans = None

    def __enter__(self):    # Łączy się z bazą danych (plikiem) i zwraca cursor do pisania zapytań w SQL lite
        self.library = sqlite3.connect(self.database)
        self.cursor = self.library.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.library.commit()
        self.library.close()

    def get_books(self):
        self.cursor.execute(
            'SELECT books.id, books.title, books.author, books.created_at '
            'FROM books '
            'LEFT JOIN book_loans ON books.id = book_loans.book_id '
            'WHERE book_loans.book_id IS NULL;'
        )

        self.books = []

        for book in self.cursor.fetchall():
            book_id, title, author, created_at = book
            self.books.append({
                'title': title,
                'author': author,
            })

        return self.books


with AccessibleBooks('baza.db') as ksiazki:
    dostępne = ksiazki.get_books()
    for pozycja in dostępne:
        print(pozycja)



