import logging

from django.conf import settings
from django.core.validators import validate_email
from django.core.mail import EmailMessage

class EmailService():
    def send_reset_password_link(self, recipient, hash_value):
        # logger        
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Wysylanie linku z resetowaniem hasla na adres " + str(recipient))

        try:
            validate_email(recipient)
            logger.info("Adres email " + recipient + " zwalidowany poprawnie")
        except Exception as e:
            logger.info(str(e))
            return False

        try:
            sender_address = settings.EMAIL_HOST_USER
            reset_password_link = settings.SITE_URL + '/reset_password/' + hash_value
            message_content = 'Link do strony resetowania hasła: <br> <a href="' + reset_password_link + '">' + reset_password_link + '</a>'

            email = EmailMessage("Resetowanie hasła", message_content, sender_address, [recipient])
            email.content_subtype = "html"
            email.send(fail_silently=False)

            logger.info("Wyslano mail z linkiem do zresetowania hasla na adres " + recipient)
            return True
        except Exception as e:
            logger.info(str(e))
            return False