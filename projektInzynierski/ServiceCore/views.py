import os
from ServiceCore.utils import createDirectoryForTaskSolutions, createSubdirectoryForAssignedGroup, createSubdirectoryForUsersInGroup, createExerciseDirectory, getExerciseDirectoryPath

from django.shortcuts import render
from django.http.response import HttpResponse

from django.contrib.auth.models import User
from django.db.models import FilePathField

from ServiceCore.models import Group, Profile, UserType, Exercise, Task, TaskType, Level, Language, Test, UnitTest

from ServiceCore.serializers import UserSerializer, GroupSerializer, ProfileSerializer, ExerciseSerializer, TaskSerializer, LevelSerializer, LanguageSerializer, TestSerializer, GroupWithAssignedTasksSerializer, TaskWithAssignedGroupsSerializer

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer


class LevelView(APIView):
    def get(self, request):
        levels = Level.objects.all()
        levelsSerializer = LevelSerializer(levels, many=True)
        return Response(levelsSerializer.data)

class LanguageView(APIView):
    def get(self, request):
        languages = Language.objects.all()
        languagesSerializer = LanguageSerializer(languages, many=True)
        return Response(languagesSerializer.data)

class ProfileView(APIView):
    def get(self, request, username):
        print(username)
        profile = Profile.objects.get(user__username=username)
        profileSerializer = ProfileSerializer(profile)
        return Response(profileSerializer.data)

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
    serializer_class = GroupWithAssignedTasksSerializer

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
        data = request.data
        
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
    
    def update(self, request, pk=None):
        data = request.data

        if pk is None:
            return Response({"message": "Nie podano parametru pk"})

        if not Group.objects.filter(name=data['oldName'], owner=request.user).exists():
            return Response({"message": "Grupa ktora chcesz edytowac nie istnieje"})
        
        try:
            groupToUpdate = Group.objects.get(name=data['oldName'])
            groupToUpdate.name = data['groupName']

            for userToAddToGroup in data['selectedUsers']:
                user = User.objects.get(username=userToAddToGroup['username'])
                groupToUpdate.users.add(user)
            groupToUpdate.save()

            for userToRemoveFromGroup in data['usersToRemove']:
                user = User.objects.get(username=userToRemoveFromGroup['username'])
                groupToUpdate.users.remove(user)
            groupToUpdate.save()
        except Exception as e:
            print(e)
            return Response({"message": "Nastąpił błąd podczas aktualizacji grupy"})
        
        return Response({"message": "Grupa została zaktualizowana"})



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
        print(request.data)
        data = request.data
        print(data)
        newExercise = None
        level = None
        language = None

        levels = Level.objects.all()
        languages = Language.objects.all()

        print()
        if not levels.filter(name=data['level']['name']).exists():
            return Response({"message": "Podano niepoprawny poziom"})

        if not languages.filter(name=data['language']['name']).exists():
            return Response({"message": "Podano niepoprawny jezyk programowania"})

        # if not data['level'].isdigit() or not data['level'] in ['1', '2', '3']:
        #    return Response({"message": "Podano niepoprawny poziom"})

        try:
            level = levels.get(name=data['level']['name'])        
            language = languages.get(name=data['language']['name'])   

            newExercise = Exercise.objects.create(author=request.user,
                                                  title=data['title'],
                                                  language=language,
                                                  content=data['content'],
                                                  level=level)
            newExercise.save()
            (message, result) = createExerciseDirectory(newExercise)

            if not result:
                print("Nie udalo sie utworzyc folderu dla obiektu Exercise")
                return Response({"message": "Nie udalo sie utworzyc folderu dla obiektu Exercise"})

            for index, unit_test in enumerate(data['unitTests']):
                print(unit_test)
                pathToExerciseDir = getExerciseDirectoryPath(newExercise)
                fileName = "unit_test" + str(index) + ".py"
                pathToFile = os.path.join(pathToExerciseDir, fileName)

                f = open(pathToFile, "w+")
                f.write("import unittest \n\
import sys \n\
class FirstTest(unittest.TestCase):\n \
    def test_first(self):\n\
        " + unit_test + "\n\
if __name__ == '__main__':\n\
    unittest.main()")

                f.close()

                # zapis sciezki w modelu nie dziala
                print(pathToFile)
                newUnitTest = UnitTest.objects.create(exercise=newExercise, pathToFile=FilePathField(path=pathToFile))
                print(newUnitTest.pathToFile)
                print(newUnitTest.pathToFile.path)
                newUnitTest.save()
                print(newUnitTest)

        except Exception as e:
            print(e)
            print("Nie udalo sie utworzyc obiektu Exercise")
            return Response({"message": "Nie udalo sie utworzyc obiektu Exercise"})

        return Response({"message": "Utworzono Exercise"})
    
    def destroy(self, request, pk=None):
        if pk is None:
            return Response({"message": "Nie podano klucza glownego cwiczenia do usuniecia"})
        
        try:
            if not Exercise.objects.filter(pk=pk).exists():
                return Response({"message": "Takie cwiczenie nie istnieje"})

            Exercise.objects.filter(pk=pk).delete()            
        except Exception as e:
            print(e)
            return Response({"message": "Nie udalo sie usunac cwiczenia"})
        
        return Response({"message": "Cwiczenie zostalo usuniete"})




class TestViewSet(viewsets.ModelViewSet):    
    permission_classes = (IsAuthenticated,)
    serializer_class = TestSerializer

    def get_queryset(self):
        queryset = None
        print(self.request.user)
        profile = Profile.objects.get(user=self.request.user)

        if profile.userType.name == "Student":
            queryset = Test.objects.all()
        else:
            queryset = self.request.user.tests.all()
        
        return queryset
    
    def create(self, request):
        print(request.data)
        data = request.data
        
        if data['title'] is None or data['exercises'] is None:
            return Response({"message": "Nie podano wszystkich danych"})

        testToCreate = None

        try:
            testToCreate = Test.objects.create(author=request.user, title=data['title'])

            for exerciseToAdd in data['exercises']:
                exercise = Exercise.objects.get(pk=exerciseToAdd['pk'])
                testToCreate.exercises.add(exercise)
            
            testToCreate.save()
        except Exception as e:
            print(e)
            print("Nastąpił błąd podczas tworzenia testu")
            return Response({"message": "Nastąpił błąd podczas tworzenia testu"})
        
        return Response({"message": "Utworzono Test"})
    
    def destroy(self, request, pk=None):
        if pk is None:
            return Response({"message": "Nie podano klucza glownego kolokwium do usuniecia"})
        
        try:
            if not Test.objects.filter(pk=pk).exists():
                return Response({"message": "Takie kolokwium nie istnieje"})

            Test.objects.filter(pk=pk).delete()            
        except Exception as e:
            print(e)
            return Response({"message": "Nie udalo sie usunac kolokwium"})
        
        return Response({"message": "Kolokwium zostalo usuniete"})

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithAssignedGroupsSerializer

    def get_queryset(self):
        queryset = None
        print(self.request.user)
        profile = Profile.objects.get(user=self.request.user)

        if profile.userType.name == "Student":
            queryset = Task.objects.all()
        else:
            queryset = self.request.user.my_tasks.all()
        
        return queryset


    def create(self, request):
        data = request.data
        print(data)
        taskType = None
        newTask = None

        try:            
            taskType = TaskType.objects.get(name=data['taskType'])

            if taskType.name == 'Test':
                test = Test.objects.get(pk=data['exercise']['pk'])
            else:
                exercise = Exercise.objects.get(pk=data['exercise']['pk'])
            groups = []

            for groupElem in data['groups']:
                group = Group.objects.get(pk=groupElem['pk'])
                groups.append(group)

            newTask = None

            if taskType.name == 'Test':
                newTask = Task.objects.create(taskType=taskType, test=test, title=data['title'], author=request.user)
            else:    
                newTask = Task.objects.create(taskType=taskType, exercise=exercise, title=data['title'], author=request.user)

            newTask.save()

            for group in groups:
                newTask.assignedTo.add(group)
            
            newTask.save()

            # tworzenie katalogu w ktorym beda odpowiednie podfoldery z rozwiazaniami
            createDirectoryForTaskSolutions(newTask)

        except Exception as e:
            print("Nie udalo sie utworzyc zadania")
            print(e)
            return Response({"message": "Nie udalo sie utworzyc zadania"})

        return Response({"message": "Zadanie zostalo utworzone"})

