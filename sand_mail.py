import smtplib
from string import Template
import sqlite3
from collections import namedtuple
from datetime import datetime

# TODO import i uzycie biblioteki: https://jinja.palletsprojects.com/en/3.1.x/intro/

# przykładowy kod do testowania mailingu w Mail Trap:
# sender = "Private Person <from@example.com>"
# receiver = "A Test User <to@example.com>"
#
# message = f"""\
# Subject: Hi Mailtrap
# To: {receiver}
# From: {sender}
#
# This is a test e-mail message."""
#
# with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
#     server.login("308f7c6fcd7f98", "********7428")   # <- Wstaw dane z Mail Trap
#     server.sendmail(sender, receiver, message)
#
# #  Przykład Template - do przerobienia na wiadomości z podstawianymi danymi naszych dłużników:
#
# wiadomosc = Template('$borrower_name nie oddałeś mi książki $book_title a termin minął $return_date!')
#
# info = [
#     ('Kuba', 'Zawód Programista', '2024-02-14'),
#     ('Leon', 'Gimnastyka dla malucha', '2024-01-29')
# ]

# for borrower_name, book_title, return_date in info:
#     text = wiadomosc.substitute(borrower_name=borrower_name, book_title=book_title, return_date=return_date)
#     print(text)

# Moj obiekt wysyłajacy maila:


class EmailSender:
    def __init__(self, database):
        self.database = database
        self.cursor = None
        self.library = None
        self.borrowed_books = None
        self.borrows = None
        self.books_after_return_date = None

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

    def send_email(self):
        borrows = self.check_books_after_return_date()

        message_content = Template(f'''
        Hej &borrower_name!
        
        Piszę do Ciebie bo jest już {datetime.today()} a umawialiśmy się,
        że książka &book_title, którą Ci pożyczyłem &borrow_date wróci do mnie do &return_date.
        
        Proszę o zwrot książki.
        
        Kuba
        ''')

        # wstawiać w miejscu "sender" mojego maila
        # wstawiać w miejscu "reciver" borrow.borrower_email

        for borrow in borrows:
            mail = message_content.substitute(
                borrower_name=borrow.borrower_name,
                book_title=borrow.book_title,
                borrow_date=borrow.borrow_date,
                return_date=borrow.return_date
            )
            sender = "Private Person <from@example.com>"
            receiver = "A Test User <to@example.com>"

            message = f"""\
            Subject: Przypomnienie o zwrocie ksiazki
            To: {receiver}
            From: {sender}
    
            {mail}"""

            with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
                server.login("************", "*******57428")  # Wstaw dane z Mail Trap
                message = message.encode('utf-8')
                server.sendmail(sender, receiver, message)
                text = 'mail wyslany :)'
        return text


with EmailSender('baza.db') as baza:
    dluznicy = baza.check_books_after_return_date()
    do_oddania = baza.send_email()
    print(dluznicy)
    print(do_oddania)
