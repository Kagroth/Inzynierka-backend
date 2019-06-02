from django.shortcuts import render
from django.http.response import HttpResponse

from django.contrib.auth.models import User
from ServiceCore.models import Group, Profile, UserType, Exercise

from ServiceCore.serializers import UserSerializer, GroupSerializer, ProfileSerializer, ExerciseSerializer

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # przeladowanie handlera metody POST -> tworzenie usera
    # aktualnie domyslnie tworzony jest student
    def create(self, request):
        data = request.data
        userType = None
        user = None

        if data['userType'] == "Student" or data['userType'] == "Teacher": 
            userType = UserType.objects.get(name=data['userType'])
        else:
            return Response({"message": "Nie udalo sie utworzyc uzytkownika danego typu"})

        try:
            if User.objects.filter(username=data['username']).exists():
                print("Uzytkownik o podanej nazwie juz istnieje")
                return Response({"message": "Uzytkownik o podanej nazwie juz istnieje"})
            
            if User.objects.filter(email=data['email']).exists():
                print("Ten email jest juz zajety")
                return Response({"message": "Ten email jest juz zajety"})

            user = User.objects.create_user(username=data['username'],
                                        first_name=data['firstname'],
                                        last_name=data['lastname'],
                                        email=data['email'],
                                        password=data['password'])
            user.save()
        except Exception as e:
            print("Nie udalo się utworzyć obiektu typu User", e)
            return Response({"message": "Blad serwera przy tworzeniu konta"})

        try: 
            profile = Profile.objects.create(user=user, userType=userType)
            profile.save()
        except:
            print("Nie udalo sie utworzyc obiektu typu Profile")
            return Response({"message": "Blad serwera przy tworzeniu konta"})

        print("Konto zostalo utworzone")
        return Response({"message": "Konto zostało utworzone"})

class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        studentType = UserType.objects.get(name="Student")
        queryset = User.objects.filter(profile__userType=studentType)
        return queryset


class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupSerializer

    # zdefiniowanie zbioru grup na podstawie rodzaju użytkownika, który żąda o dane
    def get_queryset(self):
        queryset = None
        profile = Profile.objects.get(user=self.request.user)

        if profile.userType.name == "Student":
            queryset = self.request.user.membershipGroups.all()
        else:
            queryset = self.request.user.group.all()
        
        return queryset

    # tworzenie nowej grupy
    def create(self, request):
        data = request.data['params']
        
        if Group.objects.filter(name=data['groupName'], owner=request.user).exists():
            print("Juz posiadasz grupe o takiej nazwie!")
            return Response({"message": "Juz posiadasz grupe o takiej nazwie!"})
        
        newGroup = None
        
        try:
            newGroup = Group.objects.create(name=data['groupName'], owner=request.user)

            for userToAddToGroup in data['selectedUsers']:
                user = User.objects.get(username=userToAddToGroup['username'])
                newGroup.users.add(user)
            newGroup.save()
        except:
            print("Nastąpił błąd podczas tworzenia grupy")
            return Response({"message": "Nastąpił błąd podczas tworzenia grupy"})

        return Response({"message": "Grupa została utworzona"})


class ExerciseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        queryset = None
        print(self.request.user)
        profile = Profile.objects.get(user=self.request.user)

        if profile.userType.name == "Student":
            queryset = Exercise.objects.all()
        else:
            queryset = self.request.user.exercises.all()
        
        return queryset
    
    def create(self, request):
        data = request.data['params']
        print(data)
        newExercise = None

        if not data['level'].isdigit() or not data['level'] in ['1', '2', '3']:
            return Response({"message": "Podano niepoprawny poziom"})

        try:
            newExercise = Exercise.objects.create(author=request.user,
                                                  title=data['title'],
                                                  language=data['language'],
                                                  content=data['content'],
                                                  level=data['level'])
            newExercise.save()
        except:
            print("Nie udalo sie utworzyc obiektu Exercise")
            return Response({"message": "Nie udalo sie utworzyc obiektu Exercise"})

        return Response({"message": "Utworzono Exercise"})
