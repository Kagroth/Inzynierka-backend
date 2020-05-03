
import os
from rest_framework import serializers
from django.contrib.auth.models import User
from ServiceCore.models import *
from ServiceCore.utils import getUserSolutionPath

#UnitTest model serializer
class UnitTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitTest
        fields = ('pk', 'content')

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
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'profile')
    

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
    unit_tests = UnitTestSerializer(many=True)

    class Meta:
        model = Exercise
        fields = ('pk', 'author', 'title', 'language', 'content', 'level', 'unit_tests')


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
    assigned_to = GroupSerializer()
    exercise = ExerciseSerializer()   
    test = TestSerializer()
    solutionType = SolutionTypeSerializer()
    
    class Meta:
        model = Task
        fields = ('pk', 'author', 'taskType', 'assigned_to', 'title', 'exercise', 'test', 'isActive', 'isRated', 'solutionType')


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
    assigned_to = GroupSerializer()

    class Meta:
        model = Task
        fields = ('pk', 'author', 'taskType', 'title', 'assigned_to', 'exercise', 'test', 'isActive', 'isRated', 'solutionType')

class TaskWithSolutionData(serializers.ModelSerializer):    
    author = UserSerializer()
    taskType = TaskTypeSerializer()
    exercise = ExerciseSerializer()
    test = TestSerializer()
    solutionType = SolutionTypeSerializer()   
    assigned_to = GroupSerializer() 
    solution = serializers.SerializerMethodField('getSolution')

    class Meta:
        model = Task
        fields = ('pk', 'author', 'taskType', 'title', 'assigned_to', 'exercise', 'test' ,'isActive', 'isRated','solution', 'solutionType')
    
    def getSolution(self, task):
        solution = task.solutions.all()
        return SolutionSerializer(solution, many=True).data

class SolutionExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer()    
    solution_value = serializers.SerializerMethodField('get_solution_value_from_file')
    test_results = serializers.SerializerMethodField()

    class Meta:
        model = SolutionExercise
        fields = ('pk', 'rate', 'github_link', 'solution_value', 'exercise', 'test_results')
    
    def get_solution_value_from_file(self, solution_exercise):
        sol_val = None
        solution_file_path = None

        try:
            solution_file_path = solution_exercise.pathToFile
        except Exception as e:
            print(e)
            return ""
        
        if os.path.isfile(solution_file_path):
            with open(solution_file_path, 'r') as f:
                sol_val = f.read()
            
            return sol_val
        
    def get_test_results(self, solution_exercise):
        solution = solution_exercise.solution
        test_results = None
        results_file_path = ""

        if solution.task.taskType.name == 'Exercise':
            solution_path = getUserSolutionPath(solution.task, solution.task.assigned_to, solution.user)
        else:
            solution_path = getUserSolutionPath(solution.task,
                                                solution.task.assigned_to, 
                                                solution.user, 
                                                solution_exercise.exercise)

        if solution_exercise.exercise.language.name == 'Python':
            results_file_path = os.path.join(solution_path, 'result.txt')
        else:
            results_file_path = os.path.join(solution_path, 'target', 'surefire-reports', 'UnitTest.txt')

        if os.path.isfile(results_file_path):
            try:
                with open(results_file_path, 'r') as f:
                    test_results = f.read()
            except Exception as e:
                print(str(e))

        return test_results


    

class SolutionTestSerializer(serializers.ModelSerializer):
    solution_exercises = serializers.SerializerMethodField('get_exercises_solutions')

    class Meta:
        model = SolutionTest
        fields = ('pk', 'rate', 'solution_exercises')

    def get_exercises_solutions(self, solution_test):
        solutions_exerc = solution_test.exercises_solutions.all()
        return SolutionExerciseSerializer(solutions_exerc, many=True).data

class SolutionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    task = TaskSerializer()
    solution_test = SolutionTestSerializer()
    # SolutionExerciseSerializer musi miec parametr many=True poniewaz dla False 
    # ten serializer nie zwraca poprawnie wartosci w get_solution_value_from_file
    solution_exercise = SolutionExerciseSerializer(many=True)

    class Meta:
        model = Solution
        fields = ('pk', 'user', 'task', 'rate', 'solution_test', 'solution_exercise')
