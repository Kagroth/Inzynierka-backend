
from rest_framework import serializers
from django.contrib.auth.models import User
from ServiceCore.models import Group, Profile, UserType, Exercise, Task

# UserType model serializer
class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ('name',)

# Profile model serializer
class ProfileSerializer(serializers.ModelSerializer):
    userType = UserTypeSerializer()

    class Meta:
        model = Profile
        fields = ('userType',)

# User model serializer
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'profile')
    
# ServiceCore Group model serializer 
class GroupSerializer(serializers.ModelSerializer):
    # SlugRelatedField pozwala na wypisanie polaczonych obiektow w postaci pola slug_field
    # users = serializers.SlugRelatedField(many=True, read_only=True, slug_field='username')
    
    # Nested Serializer pozwala na wypisanie obiektow w postaci zserializowanej
    users = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ('pk', 'name', 'users',)

class ExerciseSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    class Meta:
        model = Exercise
        fields = ('pk', 'author', 'title', 'language', 'content', 'level')
    
class TaskSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Task
        fields = ('pk', 'author', 'isActive')