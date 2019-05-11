from django.shortcuts import render
from django.http.response import HttpResponse

from django.contrib.auth.models import User
from ServiceCore.models import Group

from ServiceCore.serializers import UserSerializer, GroupSerializer

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer

# Create your views here.
def index(request):
    return HttpResponse("Test")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
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