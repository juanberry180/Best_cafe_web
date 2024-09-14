import smtplib
import os

my_email = os.environ.get('my_email')
email_password = os.environ.get('email_password')


class MessageSend:
    def __init__(self, contact_email, contact_text, contact_name):
        self.contact_email = contact_email
        self.contact_text = contact_text
        self.contact_name = contact_name
        self.sending_email()

    def sending_email(self):
        with smtplib.SMTP('smtp.gmail.com', 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=email_password)
            connection.sendmail(from_addr=my_email, to_addrs=my_email, msg=f"Subject:Cafe  webpage feedback.\n\n{self.contact_name.capitalize()} with email: {self.contact_email} has written:\n\n{self.contact_text}")

