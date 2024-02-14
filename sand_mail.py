import smtplib
from string import Template

# TODO import i uzycie biblioteki: https://jinja.palletsprojects.com/en/3.1.x/intro/

# przykładowy kod do testowania mailingu w Mail Trap:
sender = "Private Person <from@example.com>"
receiver = "A Test User <to@example.com>"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
    server.login("##############", "#############")   # <- Wstaw dane z Mail Trap
    server.sendmail(sender, receiver, message)

#  Przykład Template - do przerobienia na wiadomości z podstawianymi danymi naszych dłużników:

wiadomosc = Template('$borrower_name nie oddałeś mi książki $book_title a termin minął $return_date!')

info = [
    ('Kuba', 'Zawód Programista', '2024-02-14'),
    ('Leon', 'Gimnastyka dla malucha', '2024-01-29')
]

for borrower_name, book_title, return_date in info:
    text = wiadomosc.substitute(borrower_name=borrower_name, book_title=book_title, return_date=return_date)
    print(text)
