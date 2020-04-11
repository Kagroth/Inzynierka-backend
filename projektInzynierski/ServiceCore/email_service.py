from django.conf import settings
from django.core.validators import validate_email
from django.core.mail import send_mail, EmailMultiAlternatives

class EmailService():
    def send_reset_password_link(self, recipient, hash_value):
        try:
            validate_email(recipient)
        except Exception as e:
            print(str(e))
            return False
        else:
            print("Email ok")

        try:
            sender_address = settings.EMAIL_HOST_USER
            print(sender_address)
            
            msg = EmailMultiAlternatives("Temat", "Tresc wiadomosci", sender_address, [recipient])
            msg.attach_alternative('<a href="www.onet.pl">Link do strony onet pl</a>', 'text/html')
            msg.send()
        except Exception as e:
            print(e)
            pass