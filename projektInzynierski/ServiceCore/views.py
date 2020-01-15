import os
import subprocess
import shutil
import logging

from ServiceCore.models import *
from ServiceCore.serializers import *
from ServiceCore.solution_executor import *
from ServiceCore.executor import *
from ServiceCore.python_executor import *
from ServiceCore.java_executor import *
from ServiceCore.utils import *
from ServiceCore.unit_tests_utils import create_unit_tests

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import FilePathField
from django.http.response import HttpResponse
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer        

class SolutionTypeView(APIView):
    def get(self, request):
        solutionsTypes = SolutionType.objects.all()
        solTypesSerializer = SolutionTypeSerializer(solutionsTypes, many=True)
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Zwracam wszystkie obiekty SolutionType")
        return Response(solTypesSerializer.data)

class LevelView(APIView):
    def get(self, request):
        levels = Level.objects.all()
        levelsSerializer = LevelSerializer(levels, many=True)
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Zwracam wszystkie obiekty Level")
        return Response(levelsSerializer.data)

class LanguageView(APIView):
    def get(self, request):
        languages = Language.objects.all()
        languagesSerializer = LanguageSerializer(languages, many=True)
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Zwracam wszystkie obiekty Language")
        return Response(languagesSerializer.data)

class ProfileView(APIView):
    def get(self, request, username):
        print(username)
        profile = Profile.objects.get(user__username=username)
        profileSerializer = ProfileSerializer(profile)
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Zwracam profil uzytkownika: " + username)
        return Response(profileSerializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # przeladowanie handlera metody POST -> tworzenie usera
    def create(self, request):
        # komunikaty messages zwracane przez widok
        userCreationFailed = "Nie udalo sie utworzyc uzytkownika danego typu"
        usernameAlreadyExists = "Uzytkownik o podanej nazwie juz istnieje"
        emailAlreadyExists = "Ten email jest juz zajety"
        serverError = "Blad serwera przy tworzeniu konta"
        successMessage = "Konto zostało utworzone"

        # logger
        logger = logging.getLogger(self.__class__.__name__)

        # dane requesta
        data = request.data
        userType = None
        user = None

        if data['userType'] == "Student" or data['userType'] == "Teacher": 
            userType = UserType.objects.get(name=data['userType'])
        else:
            logger.info("Tworzenie uzytkownika - podano nieprawidlowy rodzaj uzytkownika")
            return Response({"message": userCreationFailed})

        try:
            if User.objects.filter(username=data['username']).exists():
                logger.info(usernameAlreadyExists)
                return Response({"message": usernameAlreadyExists}, status=400)
            
            if User.objects.filter(email=data['email']).exists():
                logger.info(emailAlreadyExists)
                return Response({"message": emailAlreadyExists})

            user = User.objects.create_user(username=data['username'],
                                        first_name=data['firstname'],
                                        last_name=data['lastname'],
                                        email=data['email'],
                                        password=data['password'])
            user.save()
        except Exception as e:
            logger.info("Nie udalo się utworzyć obiektu typu User " + e)
            return Response({"message": serverError})

        try: 
            profile = Profile.objects.create(user=user, userType=userType)
            profile.save()
        except:
            logger.info("Nie udalo sie utworzyc obiektu typu Profile")
            return Response({"message": serverError})

        logger.info(successMessage)
        return Response({"message": successMessage})

 
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
        # logger        
        logger = logging.getLogger(self.__class__.__name__)

        data = request.data
        
        if Group.objects.filter(name=data['groupName'], owner=request.user).exists():
            logger.info("Grupa o nazwie " + data['groupName'] + " juz istnieje")
            return Response({"message": "Juz posiadasz grupe o takiej nazwie!"}, status=400)
        
        newGroup = None
        
        try:
            newGroup = Group.objects.create(name=data['groupName'], owner=request.user)

            for userToAddToGroup in data['selectedUsers']:
                user = User.objects.get(username=userToAddToGroup['username'])
                newGroup.users.add(user)
            newGroup.save()
            logger.info("Grupa " + newGroup.name + " zostala utworzona")
        except:
            logger.info("Nastapil blad podczas tworzenia grupy")
            return Response({"message": "Nastąpił błąd podczas tworzenia grupy"}, status=500)

        return Response({"message": "Grupa została utworzona"}, status=200)
    
    # aktualizacja grupy o podanym pk
    def update(self, request, pk=None):
        # logger        
        logger = logging.getLogger(self.__class__.__name__)

        data = request.data

        if pk is None:
            logger.info("Nie podano parametru pk")
            return Response({"message": "Nie podano parametru pk"})

        if not Group.objects.filter(name=data['oldName'], owner=request.user).exists():
            logger.info("Grupa o nazwie " + data['oldName'] + " nie istnieje")
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
            logger.info("Grupa " + groupToUpdate + " zostala zaktualizowana")
        except Exception as e:
            logger.info("Nastapil blad podczas aktualizacji grupy " + data['oldName'] + " - " + e)
            return Response({"message": "Nastąpił błąd podczas aktualizacji grupy"})
        
        return Response({"message": "Grupa została zaktualizowana"})

    # usuniecie grupy o podanym pk
    def destroy(self, request, pk=None):
        # logger        
        logger = logging.getLogger(self.__class__.__name__)

        data = request.data

        if pk is None:
            logger.info("Nie podano parametru pk")
            return Response({"message": "Nie podano parametru pk"})

        if Group.objects.filter(pk=pk).exists():
            Group.objects.filter(pk=pk).delete()
            logger.info("Grupa o pk=" + pk + " zostala usunieta")
            return Response({"message": "Grupa zostala usunieta"})
        else:
            logger.info("Nie udalo sie usunac grupy o pk=" + pk)
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
        # logger        
        logger = logging.getLogger(self.__class__.__name__)

        print(request.data)
        data = request.data
        print(data)
        newExercise = None
        level = None
        language = None

        levels = Level.objects.all()
        languages = Language.objects.all()

        
        if Exercise.objects.filter(title=data['title'], author=request.user).exists():
            logger.info("Cwiczenie o tytule" + data['title'] + " juz istnieje")
            return Response({"message": "Cwiczenie o takim tytule juz istnieje"}, status=400)

        if not levels.filter(name=data['level']['name']).exists():
            logger.info("Poziom " + data['level']['name'] + " nie istnieje")
            return Response({"message": "Podano niepoprawny poziom"})

        if not languages.filter(name=data['language']['name']).exists():
            logger.info("Jezyk programowania " + data['language']['name'] + " nie istnieje")
            return Response({"message": "Podano niepoprawny jezyk programowania"})

        try:
            level = levels.get(name=data['level']['name'])        
            language = languages.get(name=data['language']['name'])   

            newExercise = Exercise.objects.create(author=request.user,
                                                  title=data['title'],
                                                  language=language,
                                                  content=data['content'],
                                                  level=level)
           

            if not createExerciseRootDirectory(newExercise):
                logger.info("Nie udalo sie utworzyc folderu dla obiektu Exercise")
                return Response({"message": "Nie udalo sie utworzyc folderu dla obiektu Exercise"}, status=500)
            
            newExercise.save()

            logger.info("Cwiczenie zostalo utworzone")
            
            create_unit_tests(newExercise, data['unitTests'])

        except Exception as e:
            logger.info("Nie udalo sie utworzyc obiektu Exercise - " + e)
            return Response({"message": "Nie udalo sie utworzyc obiektu Exercise"}, status=500)

        return Response({"message": "Utworzono Exercise"}, status=200)
    
    # usuwanie cwiczenia o podanym pk
    def destroy(self, request, pk=None):
        # logger        
        logger = logging.getLogger(self.__class__.__name__)

        if pk is None:
            logger.info("Nie podano klucza glownego cwiczenia ktore ma zostac usuniete")
            return Response({"message": "Nie podano klucza glownego cwiczenia do usuniecia"})
        
        try:
            if not Exercise.objects.filter(pk=pk).exists():
                logger.info("Cwiczenie o pk=" + pk + " nie istnieje")
                return Response({"message": "Takie cwiczenie nie istnieje"})

            print("Pobier cwiczenie")
            logger.info("Pobranie cwiczenia o pk=" + pk)
            exerciseTodelete = Exercise.objects.filter(pk=pk).get()
            logger.info("Pobranie sciezki do folderu z cwiczeniem o pk=" + pk)
            pathToExercise = getExerciseDirectoryRootPath(exerciseTodelete)
            
            logger.info("Usuwanie folderu - " + pathToExercise)
            
            if os.path.exists(pathToExercise):
                shutil.rmtree(pathToExercise)
            else:
                logger.info("Folder " + pathToExercise + " nie istnieje wiec nie mozna go usunac")

            exerciseTodelete.delete()   
            logger.info("Cwiczenie o pk=" + pk + " zostalo usuniete")         
        except Exception as e:
            logger.info("Nie udalo sie usunac cwiczenia o pk=" + pk + " - " + e)
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
        #logger
        logger = logging.getLogger(self.__class__.__name__)
        
        print(request.data)
        data = request.data
        
        if data['title'] is None or data['exercises'] is None:
            return Response({"message": "Nie podano wszystkich danych"}, status=400)

        if Test.objects.filter(title=data['title'], author=request.user).exists():
            logger.info("Kolokwium o tytule" + data['title'] + " juz istnieje")
            return Response({"message": "Kolokwium o takim tytule juz istnieje"}, status=400)
        
        testToCreate = None

        try:
            testToCreate = Test.objects.create(author=request.user, title=data['title'])

            for exerciseToAdd in data['exercises']:
                exercise = Exercise.objects.get(pk=exerciseToAdd['pk'])
                testToCreate.exercises.add(exercise)
            
            #createTestDirectory(testToCreate)
            if createTestRootDirectory(testToCreate):
                testToCreate.save()
            else:
                testToCreate.delete()
                return Response({"message": "Nie udalo sie utworzyc testu - blad tworzenia katalogow"}, status=500)

        except Exception as e:
            print(e)
            print("Nastąpił błąd podczas tworzenia testu")
            return Response({"message": "Nastąpił błąd podczas tworzenia testu"}, status=500)
        
        return Response({"message": "Utworzono Test"}, status=200)
    
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
        logger = logging.getLogger(__name__)
        queryset = None

        profile = Profile.objects.get(user=self.request.user)

        logger.info("Uzytkownik " + str(self.request.user.username) + " - " + profile.userType.name + " pobiera zadania")

        if profile.userType.name == "Student":
            groups = self.request.user.membershipGroups.all()            

            if groups.count() > 0:
                queryset = groups[0].tasks.all()

                for group in groups:
                    queryset = queryset.union(group.tasks.all())
                
                queryset = queryset.distinct()

            else:
                queryset = queryset.none()

        else:
            queryset = self.request.user.my_tasks.all()
        
        return queryset


    # utworz zadanie
    def create(self, request):
        # logger
        logger = logging.getLogger(self.__class__.__name__)

        # dane
        data = request.data
        print(data)

        taskType = None
        newTask = None
        solutionType = None

        try:            
            taskType = TaskType.objects.get(name=data['taskType'])

            if taskType.name == 'Test':
                test = Test.objects.get(pk=data['exercise']['pk'])
            else:
                exercise = Exercise.objects.get(pk=data['exercise']['pk'])            

            group = Group.objects.get(pk=data['group']['pk'])
            
            if Task.objects.filter(title=data['title'], author=request.user).exists():
                logger.info("Zadanie o tytule" + data['title'] + " juz istnieje")
                return Response({"message": "Zadanie o takim tytule juz istnieje"}, status=400)
            
            newTask = None

            if taskType.name == 'Test':
                newTask = Task.objects.create(taskType=taskType, test=test, title=data['title'], author=request.user)
            else:    
                newTask = Task.objects.create(taskType=taskType, exercise=exercise, title=data['title'], author=request.user)

            solutionType = SolutionType.objects.get(name=data['solutionType']['name'])
            newTask.solutionType = solutionType

            newTask.save()

            newTask.assignedTo.add(group)
            
            newTask.save()

            # tworzenie katalogu w ktorym beda odpowiednie podfoldery z rozwiazaniami
            createDirectoryForTaskSolutions(newTask)

        except Exception as e:
            print(e)
            logger.info("Nie udalo sie utworzyc zadania - " + str(e))
            return Response({"message": "Nie udalo sie utworzyc zadania"}, status=500)

        logger.info("Zadanie zostalo utworzone")
        return Response({"message": "Zadanie zostalo utworzone"}, status=200)
    
    def update(self, request, pk=None):
        # logger
        logger = logging.getLogger(self.__class__.__name__)
        data = request.data

        if data['mode'] == 'CLOSE':
            # zamykanie zadania - niemozliwe bedzie wysylanie odpowiedzi
            try:
                taskToClose = Task.objects.get(pk=data['pk'])
                taskToClose.isActive = False
                taskToClose.save()

                logger.info("Zamknieto zadanie o pk=" + str(data['pk']))

                return Response({"message": "Zamknieto zadanie"}, status=200)
            except Exception as e:
                logger.info("Nie udalo sie zamknac zadania o pk=" + str(data['pk']) + ". Blad=" + str(e))

                return Response({"message": "Nie udalo sie zamknac zadania"}, status=500)

        return Response({"message": "UPDATE ZAKONCZONY"}, status=200)

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
        # pobranie pierwszej grupy - niepotrzebne 
        # print(solution.user.membershipGroups.all()[:1].get())

        serializer = SolutionSerializer(solution)
        newdict = {}
        solutionValue = None

        if solution.task.taskType.name == 'Exercise':
            solution_file_path = solution.solution_exercise.get().pathToFile

            if os.path.isfile(solution_file_path):
                with open(solution_file_path, 'r') as f:
                    solutionValue = f.read()
        else:
            solutionValue = []

            for solution_exercise in solution.solution_test.exercises_solutions.all():
                solution_file_path = solution_exercise.pathToFile
                
                if os.path.isfile(solution_file_path):
                    with open(solution_file_path, 'r') as f:
                        solutionValue.append(f.read())
       
        newdict['solutionValue'] = solutionValue
        print(newdict)
        newdict.update(serializer.data)

        return Response(newdict)
    
    # tworzenie rozwiazania i testowanie:
    # aktualne obslugiwane metody rozwiazania:
    #   - przeslanie pliku
    #   - edytor
    def create(self, request):
        data = request.data
        print(data)
        print(data['solutionType'])     

        task = Task.objects.get(pk=data['taskPk'])

        # tworzenie glownego obiektu Solution
        Solution.objects.update_or_create(task=task, user=request.user)

        exercise = None

        if task.taskType.name == 'Exercise':
            exercise = task.exercise
        else:
            exercise = task.test.exercises.get(pk=data['exercisePk'])

        concreteExecutor = None

        if exercise.language.name == 'Python':
            concreteExecutor = PythonExecutor()
        elif exercise.language.name == 'Java':
            concreteExecutor = JavaExecutor()

        concreteExecutor.configure(request.user, task, data)
        
        solExecutor = Executor(concreteExecutor)
        
        (result, message) = solExecutor.execute()

        print(result)
        print(message)

        return Response({"message": message, "test_results": solExecutor.get_result()})