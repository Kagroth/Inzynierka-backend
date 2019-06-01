from django.shortcuts import render
from django.http.response import HttpResponse

from django.contrib.auth.models import User
from ServiceCore.models import Group, Profile, UserType

from ServiceCore.serializers import UserSerializer, GroupSerializer

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer

# Create your views here.
def index(request):
    return HttpResponse("Test")

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

class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request):
        data = request.data['params']
        
        newGroup = Group.objects.create(name=data['groupName'])

        for userToAddToGroup in data['selectedUsers']:
            user = User.objects.get(username=userToAddToGroup['username'])
            newGroup.users.add(user)

        return Response({"message": "sukces"})
    
'''
class ListUsers(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        usersSet = User.objects.all()
        # tlumaczenie obiektow na dict
        usersSetSerialized = UserSerializer(usersSet, many=True)
        # konwersja dict na json
        #usersSetJson = JSONRenderer().render(usersSetSerialized.data)

        return Response(usersSetSerialized.data)

class ListGroup(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        groupSet = Group.objects.all()
        groupSetSerialized = GroupSerializer(groupSet, many=True)

        return Response(groupSetSerialized.data)
'''