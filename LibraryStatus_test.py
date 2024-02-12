from unittest.mock import patch
import pytest
import sqlite3
from LibraryStatus import LibraryStatus


# @pytest.fixture()
def create_data_base():
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()
    cursor.execute('''
            CREATE TABLE books
            (id INTEGER, title TEXT, author TEXT, created_at DATE)''')
    sample_data = [
        (1, 'Atomic Habits', 'James Clear', '2019-05-23 16:50:30'),
        (10, 'Nawyk Samodyscypliny', 'Neil Fiore', '2022-01-19 22:59:30')]
    cursor.executemany('INSERT INTO books VALUES(?, ?, ?, ?)', sample_data)
    return cursor


# zrób testy wszystkich metod klasy LibraryStatus
class TestLibraryStatus():

    def test_get_all_books_positive(self):
        with patch("LibraryStatus.__enter__", return_value=create_data_base()):
            library = LibraryStatus(create_data_base())

            library.get_all_books()

            assert library.all_books[0] == (1, 'Atomic Habits', 'James Clear', '2019-05-23 16:50:30')
        # TODO


def test_get_borrowers_negative():
    pass
