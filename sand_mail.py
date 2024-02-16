import smtplib
from string import Template
import sqlite3
from collections import namedtuple
from datetime import datetime

# TODO import i uzycie biblioteki: https://jinja.palletsprojects.com/en/3.1.x/intro/
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
        Hej $borrower_name!
        
        Pisze do Ciebie bo jest juz {datetime.strftime(datetime.today(), format='%Y-%m-%d')} a umawialismy sie,
        ze ksiazka $book_title, ktora Ci pozyczylem $borrow_date wroci do mnie do $return_date.
        
        Prosze o zwrot ksiazki.
        
        Kuba
        ''')

        # wstawiać w miejscu "sender" mojego maila
        # wstawiać w miejscu "reciver" borrow.borrower_email

        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.login("*******", "*********")  # Wstaw dane z Mail Trap

            for borrow in borrows:  # TODO aktuanie pomija znaki ale to lipa jest:
                mail = message_content.substitute(
                    borrower_name=str(borrow.borrower_name),
                    book_title=str(borrow.book_title.encode('ascii', 'ignore').decode('ascii')),
                    borrow_date=str(borrow.borrow_date),
                    return_date=str(borrow.return_date)
                )

                sender = "Private Person <from@example.com>"
                receiver = "A Test User <to@example.com>"

                message = f"""\
                Subject: Przypomnienie o zwrocie ksiazki
                To: {receiver}
                From: {sender}
        
                 {mail}"""

                server.sendmail(sender, receiver, message)

                text = f'Mail o tresci:\n{message} \n Mail zostal wyslany :)'
        return text


with EmailSender('baza.db') as baza:
    dluznicy = baza.check_books_after_return_date()
    do_oddania = baza.send_email()
    print(dluznicy)
    print(do_oddania)
