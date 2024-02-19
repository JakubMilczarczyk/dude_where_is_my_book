from email.mime.text import MIMEText
import smtplib
import ssl
from string import Template
import sqlite3
from collections import namedtuple
from datetime import datetime


# TODO import i uzycie biblioteki: https://jinja.palletsprojects.com/en/3.1.x/intro/
# Moj obiekt wysyłajacy maila:


class EmailSender:
    def __init__(self, database, port, smtp_address, ssl_enabled=False):
        self.database = database
        self.cursor = None
        self.library = None
        self.borrowed_books = None
        self.borrows = None
        self.books_after_return_date = None
        self.port = int(port)
        self.smtp_address = smtp_address
        self.ssl_enabled = ssl_enabled

    def __enter__(self):
        self.library = sqlite3.connect(self.database)
        self.cursor = self.library.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.library.commit()
        self.library.close()

    def check_books_after_return_date(self):
        self.books_after_return_date = []

        self.cursor.execute('''
            SELECT borrowers.name, borrowers.email, books.title, 
            borrowed_books.borrow_date, borrowed_books.return_date 
            FROM borrowed_books 
            JOIN borrowers ON borrowed_books.borrower_id = borrowers.id 
            JOIN books ON borrowed_books.book_id = books.id;
        ''')

        for loan in self.cursor.fetchall():
            Borrow = namedtuple(
                'Borrow',
                [
                    'borrower_name',
                    'borrower_email',
                    'book_title',
                    'borrow_date',
                    'return_date'

                ]
            )
            if datetime.strptime(str(loan[-1]), '%Y-%m-%d') < datetime.today():
                self.books_after_return_date.append(Borrow(*loan))

        return self.books_after_return_date

    def send_email(self):   # TODO wywalić to do osobnej klasy albo zamienić tą na email context manager + inna klasa
                            # np metodę check_books_after_return_date() brać z klasy LibraryStatus
        borrows = self.check_books_after_return_date()

        message_content = Template(f'''
        Hej $borrower_name!
        
        Piszę do Ciebie bo jest już {datetime.strftime(datetime.today(), format='%Y-%m-%d')} a umawialiśmy sie,
        że książka $book_title, którą Ci pożyczyłem $borrow_date wróci do mnie do $return_date.
        
        Proszę o zwrot książki.
        
        Kuba
        ''')

        # wstawiać w miejscu "sender" mojego maila
        # wstawiać w miejscu "reciver" borrow.borrower_email
        with smtplib.SMTP(f"smtp.{self.smtp_address}", self.port) as connection:

            for borrow in borrows:
                mail = message_content.substitute(
                    borrower_name=borrow.borrower_name,
                    book_title=borrow.book_title,
                    borrow_date=borrow.borrow_date,
                    return_date=borrow.return_date
                )

                sender = "Private Person <from@example.com>"
                receiver = "A Test User <to@example.com>"

                message = MIMEText(f"{mail}")
                message['Subject'] = 'Przypomnienie o zwrocie książki'
                message['To'] = receiver
                message['From'] = sender

                message = message.as_string()

                if not self.ssl_enabled:
                    connection = connection
                else:
                    context = ssl.create_default_context()
                    connection = smtplib.SMTP_SSL(f"smtp.{self.smtp_address}", self.port, context=context)

                connection.login("*****", "*********")    # Wstaw dane z Mail Trap
                connection.sendmail(sender, receiver, message)

                text = f'Mail o treści:\n{message} \n Mail został wysłany :)'
                return text


with EmailSender('baza.db', '2525', 'mailtrap.io') as baza:
    dluznicy = baza.check_books_after_return_date()
    do_oddania = baza.send_email()
    print(dluznicy)
    print(do_oddania)
