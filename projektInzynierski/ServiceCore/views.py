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
        userType = UserType.objects.get(name="Student")
        user = User.objects.create_user(username=data['username'],
                                        first_name=data['firstname'],
                                        last_name=data['lastname'],
                                        email=data['email'],
                                        password=data['password'])
        user.save()
        profile = Profile.objects.create(user=user, userType=userType)
        profile.save()
        return Response({"message": "Dupa"})

class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
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