import pytest
import sqlite3
from LibraryStatus import LibraryStatus

# zrób testy wszystkich metod klasy LibraryStatus

@pytest.fixture()
def create_data_base():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE books
            (id INTEGER, title TEXT, author TEXT, created_at DATE)''')
    sampe_data = [
        (1, 'Atomic Habits', 'James Clear', '2019-05-23 16:50:30'),
        (10, 'Nawyk Samodyscypliny', 'Neil Fiore', '2022-01-19 22:59:30')]
    cursor.executemany('INSERT INTO books VALUES(?, ?, ?, ?)', sampe_data)
    return cursor


def test_get_all_books_positive(create_data_base):
    # given
    # conn = sqlite3.connect(':memory:')
    # cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE books
    #     (id INTEGER, title TEXT, author TEXT, created_at DATE)''')
    # sampe_data = [
    #     (1, 'Atomic Habits', 'James Clear', '2019-05-23 16:50:30'),
    #     (10, 'Nawyk Samodyscypliny', 'Neil Fiore', '2022-01-19 22:59:30')]
    # cursor.executemany('INSERT INTO books VALUES(?, ?, ?, ?)', sampe_data )

    library = LibraryStatus(create_data_base)
    # when:
    library.get_all_books()

    # then:
    assert library.all_books[0] == (1, 'Atomic Habits', 'James Clear', '2019-05-23 16:50:30')
    # TODO


def test_get_borrowers_negative():
    pass


