
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
    # SlugRelatedField pozwala na wypisanie polaczonych obiektow w postaci pola slug_field
    # users = serializers.SlugRelatedField(many=True, read_only=True, slug_field='username')
    
    # Nested Serializer pozwala na wypisanie obiektow w postaci zserializowanej
    
    users = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ('name', 'users',)
