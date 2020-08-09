from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.db import transaction
from ServiceCore.models import Profile, UserType

class Command(BaseCommand):
    help = "Tworzy konto nauczyciela"

    def add_arguments(self, parser):
        # imie
        # nazwisko
        # nazwa uzytkownika
        # email
        # haslo
        # parser.add_argument()
        parser.add_argument("firstname", help="Imie")
        parser.add_argument("lastname", help="Nazwisko")
        parser.add_argument("email", help="Adres email")        
        parser.add_argument("username", help="Nazwa użytkownika - co najmniej 3 znaki")
        parser.add_argument("password", help="Hasło - co najmniej 8 znaków")

    def handle(self, *args, **options):
        try:
            validate_email(options['email'])
        except Exception as e:
            self.stderr.write("Niepoprawny adres email")
            self.stderr.write(str(e))
            return
        
        if len(options['username']) < 3:
            self.stdout.write("Nazwa użytkownika musi się składać z co najmniej 3 znaków")
            return
        
        if len(options['password']) < 8:
            self.stdout.write("Hasło musi się składać z co najmniej 8 znaków")
            return

        try:
            with transaction.atomic():
                userType = UserType.objects.get(name="Teacher")
                
                if User.objects.filter(username=options['username']).exists():
                    self.stderr.write("Nazwa uzytkownika jest zajeta")
                    return
                
                if User.objects.filter(email=options['email']).exists():
                    self.stderr.write("Email jest juz zajety")    
                    return
                
                user = User.objects.create_user(username=options['username'],
                                            first_name=options['firstname'],
                                            last_name=options['lastname'],
                                            email=options['email'],
                                            password=options['password'])
                user.save()

                profile = Profile.objects.create(user=user, userType=userType)
                profile.save()

            self.stdout.write("Konto nauczyciela zostało utworzone")    
            return
        except Exception as identifier:
            self.stderr.write(str(identifier))
            return