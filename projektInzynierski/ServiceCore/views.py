import os
import subprocess
import shutil

from ServiceCore.utils import *
from ServiceCore.unit_tests_utils import create_unit_tests

from django.shortcuts import render
from django.http.response import HttpResponse

from django.contrib.auth.models import User
from django.db.models import FilePathField
from django.core.files.storage import FileSystemStorage

from ServiceCore.models import *

from ServiceCore.serializers import *

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

# 
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
    
    # aktualizacja grupy o podanym pk
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

    # usuniecie grupy o podanym pk
    def destroy(self, request, pk=None):
        data = request.data

        if pk is None:
            return Response({"message": "Nie podano parametru pk"})

        if Group.objects.filter(pk=pk).exists():
            Group.objects.filter(pk=pk).delete()
            return Response({"message": "Grupa zostala usunieta"})
        else:
            return Response({"message": "Nie udalo sie usunac grupy"})



# viewset z cwiczeniami
class ExerciseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = ExerciseSerializer

    def get_queryset(self):
        queryset = None
        print(self.request.user)
        profile = Profile.objects.get(user=self.request.user)

        if profile.userType.name == "Student":
            # student nie powinien miec mozliwosci ogladania cwiczen, teoretycznie
            # wglad do nich powinien byc jedynie poprzez Task
            queryset = Exercise.objects.all()
        else:
            queryset = self.request.user.exercises.all()
        
        return queryset
    
    # tworzenie cwiczenia
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

        try:
            level = levels.get(name=data['level']['name'])        
            language = languages.get(name=data['language']['name'])   

            newExercise = Exercise.objects.create(author=request.user,
                                                  title=data['title'],
                                                  language=language,
                                                  content=data['content'],
                                                  level=level)
            newExercise.save()
            # (message, result) = createExerciseDirectory(newExercise)
            if not createExerciseRootDirectory(newExercise):
                print("Nie udalo sie utworzyc folderu dla obiektu Exercise")
                return Response({"message": "Nie udalo sie utworzyc folderu dla obiektu Exercise"})

            create_unit_tests(newExercise, data['unitTests'])

        except Exception as e:
            print(e)
            print("Nie udalo sie utworzyc obiektu Exercise")
            return Response({"message": "Nie udalo sie utworzyc obiektu Exercise"})

        return Response({"message": "Utworzono Exercise"})
    
    # usuwanie cwiczenia o podanym pk
    def destroy(self, request, pk=None):
        if pk is None:
            return Response({"message": "Nie podano klucza glownego cwiczenia do usuniecia"})
        
        try:
            if not Exercise.objects.filter(pk=pk).exists():
                return Response({"message": "Takie cwiczenie nie istnieje"})

            print("Pobier cwiczenie")
            exerciseTodelete = Exercise.objects.filter(pk=pk).get()
            print("Pobieram sciezke do folderu z cwiczeniem")
            pathToExercise = getExerciseDirectoryRootPath(exerciseTodelete)
            print("Usuwam folder - " + pathToExercise)
            if os.path.exists(pathToExercise):
                shutil.rmtree(pathToExercise)
            else:
                print("Nie ma takiego folderu")
            print("Usuwam cwiczenie")
            exerciseTodelete.delete()   
            print("usuniete")         
        except Exception as e:
            print(e)
            return Response({"message": "Nie udalo sie usunac cwiczenia"})
        
        return Response({"message": "Cwiczenie zostalo usuniete"})




# viewset z kolokwiami
class TestViewSet(viewsets.ModelViewSet):    
    permission_classes = (IsAuthenticated,)
    serializer_class = TestSerializer

    def get_queryset(self):
        queryset = None
        print(self.request.user)
        profile = Profile.objects.get(user=self.request.user)

        if profile.userType.name == "Student":
            # student nie powinien miec mozliwosci ogladania kolokwium, teoretycznie
            # wglad do nich powinien byc jedynie poprzez Task
            queryset = Test.objects.all()
        else:
            queryset = self.request.user.tests.all()
        
        return queryset
    
    # utworz kolokwium
    # tu dopisac tworzenie folderow dla kolokwium
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
            
            #createTestDirectory(testToCreate)
            createTestRootDirectory(testToCreate)
            testToCreate.save()

        except Exception as e:
            print(e)
            print("Nastąpił błąd podczas tworzenia testu")
            return Response({"message": "Nastąpił błąd podczas tworzenia testu"})
        
        return Response({"message": "Utworzono Test"})
    
    # usun kolokwium o podanym pk
    # tu dopisac usuwanie folderu
    def destroy(self, request, pk=None):
        if pk is None:
            return Response({"message": "Nie podano klucza glownego kolokwium do usuniecia"})
        
        try:
            if not Test.objects.filter(pk=pk).exists():
                return Response({"message": "Takie kolokwium nie istnieje"})

            testToDelete = Test.objects.filter(pk=pk).get()
            pathToTest = getTestDirectoryRootPath(testToDelete)
            
            if os.path.exists(pathToTest):
                shutil.rmtree(pathToTest)
            else:
                print("Nie ma takiego folderu")
            
            testToDelete.delete()

        except Exception as e:
            print(e)
            return Response({"message": "Nie udalo sie usunac kolokwium"})
        
        return Response({"message": "Kolokwium zostalo usuniete"})

# viewset z zadaniami przydzielanymi studentom
class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaskWithSolutionData

    def get_queryset(self):
        queryset = None
        print(self.request.user)
        profile = Profile.objects.get(user=self.request.user)

        if profile.userType.name == "Student":
            queryset = Task.objects.all()
            groups = self.request.user.membershipGroups.all()

            if groups.count() > 0:
                for group in groups:
                    queryset.filter(assignedTo=group)
            else:
                queryset = queryset.none()

        else:
            queryset = self.request.user.my_tasks.all()
        
        print(queryset)
        return queryset


    # utworz zadanie
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

# viewset z rozwiazaniami zadan
class SolutionViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SolutionSerializer

    def get_queryset(self):
        queryset = None
        return Solution.objects.all()
        profile = Profile.objects.get(user=self.request.user)

        if profile.userType.name == "Student":        
            queryset = Solution.objects.filter(user=self.request.user)
        else:
            queryset = Solution.objects.all()

        return queryset
    
    # zwroc rozwiazanie o podanym pk
    def retrieve(self, request, pk=None):
        queryset = Solution.objects.all()
        solution = queryset.get(pk=pk)
        # pobranie pierwszej grupy
        print(solution.user.membershipGroups.all()[:1].get())
        serializer = SolutionSerializer(solution)
        newdict = {}
        solutionPath = ""

        for group in solution.user.membershipGroups.all():
            solutionPath = getUserSolutionPath(solution.task,
                                           group,
                                           solution.user)

            solutionPath = os.path.join(solutionPath, 'solution.py')
            print(solutionPath)
            if os.path.isfile(solutionPath):
                f = open(solutionPath, "r")
                newdict['solutionValue'] = f.read()
                f.close()        
                break
        
        print(newdict)
        newdict.update(serializer.data)
        return Response(newdict)
    
    # tworzenie rozwiazania i testowanie:
    # aktualne obslugiwane metody rozwiazania:
    #   - przeslanie pliku
    def create(self, request):
        data = request.data
        print(data)
        print(data['file'])
        print(request.FILES)

        task = Task.objects.get(pk=data['taskPk'])
        exercise = task.exercise

        fileToSave = request.FILES['file']
        fs = FileSystemStorage()

        for group in task.assignedTo.all():
            fs.location = getUserSolutionPath(task, group, request.user)
            fileToSave.name = 'solution.py'
            destinatedPath = os.path.join(fs.location, fileToSave.name)

            if os.path.isfile(destinatedPath):
                os.remove(destinatedPath)
             
            fs.save(fileToSave.name, fileToSave)

        exercisePath = getExerciseDirectoryRootPath(exercise)
        testResults = []

        if os.path.isdir(exercisePath):
            for subdir, dirs, files in os.walk(exercisePath):
                for file in files:
                    if os.path.isfile(os.path.join(subdir, file)):
                        print (os.path.join(subdir, file))
                        # skopiowanie unit testow 
                        copyCommand = 'copy ' + str(os.path.join(subdir, file)) + ' ' + str(os.path.join(fs.location, file))
                        print(copyCommand)
                        print("")
                        os.popen(copyCommand)
                        # polecenie uruchamiajace testy, mozna wyniesc po za petle
                        test_command = 'python -m unittest discover -v -s ' + fs.location
                        print(test_command)
                        rfile = open(os.path.join(fs.location, "result.txt"), "w")
                        # uruchomienie testow
                        process = subprocess.run(test_command, capture_output=True)
                        print(process.returncode)
                        print(process.stdout)
                        print(process.stderr.decode("utf-8"))
                        # zapis wyniku testow do pliku results.txt
                        rfile.write(process.stderr.decode("utf-8"))
                        rfile.close()

        newSolution, created = Solution.objects.update_or_create(task=task, user=request.user, pathToFile=fs.location, rate=2)
        newSolution.save()
        return Response({"message": "Pomyslnie zapisano rozwiazanie", "test_results": testResults})