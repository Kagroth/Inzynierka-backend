
from rest_framework import serializers
from django.contrib.auth.models import User
from ServiceCore.models import *

# SolutionType model serializer

class SolutionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionType
        fields = ('name',)

# Language model serializer
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('name', 'allowed_extension')


# Level model serializer
class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('name',)


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
        fields = ('pk', 'name', 'users')


class ExerciseSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    language = LanguageSerializer()
    level = LevelSerializer()

    class Meta:
        model = Exercise
        fields = ('pk', 'author', 'title', 'language', 'content', 'level')


class TestSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True)
    class Meta:
        model = Test
        fields = ('pk', 'title', 'exercises')

class TaskTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskType
        fields = ('pk', 'name')


class TaskSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    taskType = TaskTypeSerializer()
    exercise = ExerciseSerializer()   
    test = TestSerializer()
    solutionType = SolutionTypeSerializer()
    
    class Meta:
        model = Task
        fields = ('pk', 'author', 'taskType', 'title', 'exercise', 'test', 'isActive', 'solutionType')


class GroupWithAssignedTasksSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True)
    activeTasks = serializers.SerializerMethodField('getActiveTasks') # wyswietla zadania ktore sa przypisane do grup
    archivedTasks = serializers.SerializerMethodField('getArchivedTasks') # wyswietla zadania nieaktywne juz

    class Meta:
        model = Group
        fields = ('pk', 'name', 'users', 'activeTasks', 'archivedTasks')

    def getActiveTasks(self, group):
        activeTasks = group.tasks.filter(isActive=True)
        return TaskSerializer(activeTasks, many=True).data
    
    def getArchivedTasks(self, group):
        archivedTasks = group.tasks.filter(isActive=False)
        return TaskSerializer(archivedTasks, many=True).data


class TaskWithAssignedGroupsSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    taskType = TaskTypeSerializer()
    exercise = ExerciseSerializer()
    test = TestSerializer()   
    solutionType = SolutionTypeSerializer()
    assignedTo = GroupSerializer(many=True) # wyswietlenie grup do ktorych zostalo przypisane zadanie 

    class Meta:
        model = Task
        fields = ('pk', 'author', 'taskType', 'title', 'assignedTo', 'exercise', 'test', 'isActive', 'solutionType')

class TaskWithSolutionData(serializers.ModelSerializer):    
    author = UserSerializer()
    taskType = TaskTypeSerializer()
    exercise = ExerciseSerializer()
    test = TestSerializer()
    solutionType = SolutionTypeSerializer()   
    assignedTo = GroupSerializer(many=True) # wyswietlenie grup do ktorych zostalo przypisane zadanie 
    solution = serializers.SerializerMethodField('getSolution')

    class Meta:
        model = Task
        fields = ('pk', 'author', 'taskType', 'title', 'assignedTo', 'exercise', 'test' ,'isActive', 'solution', 'solutionType')
    
    def getSolution(self, task):
        solution = task.solutions.all()
        return SolutionSerializer(solution, many=True).data

class SolutionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    task = TaskSerializer()

    class Meta:
        model = Solution
        fields = ('pk', 'user', 'task', 'rate')

