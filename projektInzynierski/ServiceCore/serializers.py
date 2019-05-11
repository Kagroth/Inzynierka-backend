
from rest_framework import serializers
from django.contrib.auth.models import User
from ServiceCore.models import Group

# User serializer model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
    
# ServiceCore Group serializer model
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name')
