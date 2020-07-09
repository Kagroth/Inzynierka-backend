import os
import subprocess
import shutil
import logging
import time

from ServiceCore.email_service import EmailService
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
from django.core.signing import Signer
from django.db.models import FilePathField
from django.db import transaction
from django.http.response import HttpResponse
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer        

class MavenTestView(APIView):
    def get(self, request):
        test_command = ['mvn', 'clean', 'test']
        
        shell = request.GET.get('shell')
        print(shell)
        shell = bool(shell)
        print(shell)
        
        process = None

        try:
            process = subprocess.run(test_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        except Exception as e:
            message = str(e)
            print(message)
            return Response({"err": message})

        process_out = process.stdout.decode("utf-8", errors="ignore")           
        process_err = process.stderr.decode("utf-8", errors="ignore")
        
        return Response({"out": process_out, "err": process_err})

# zwraca liste studentow ktorzy sa czlonkami grup nauczyciela wysylajacego request 
class TeachersStudentsView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        logger = logging.getLogger(__name__)   
        
        queryset = User.objects.none()

        groups = self.request.user.group.all()

        for group in groups:
            queryset = queryset.union(group.users.all())
        
        queryset = queryset.distinct()

        serializer_data = UserSerializer(queryset, many=True)

        return Response(serializer_data.data)

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

    def retrieve(self, request, pk=None):
        # logger        
        logger = logging.getLogger(self.__class__.__name__)

        if pk is None:
            return Response({"message": "Nie podano nazwy uzytkownika"}, status=400)
        
        try:
            user = User.objects.get(pk=pk)        
            user_serializer = UserSerializer(user)
            solutions_serializer = SolutionSerializer(user.solutions.all(), many=True)

            groups = user.membershipGroups.all()            
            tasks = Task.objects.none()

            for group in groups:
                tasks = tasks.union(group.tasks.all())

            tasks = tasks.distinct()

            tasks_with_solutions_serializer = TaskWithSolutionData(tasks, many=True)
            response_data = {}        
            response_data['solutions'] = solutions_serializer.data
            response_data['user'] = user_serializer.data
            response_data['tasks'] = tasks_with_solutions_serializer.data

            return Response(response_data, status=200)
        except Exception as e:
            logger.info("Blad pobierania uzytkownika: " + str(e))
            return Response({"message": "Blad pobierania uzytkownika"}, status=500)

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

        if data['userType'] == "Student": 
            userType = UserType.objects.get(name=data['userType'])
        else:
            logger.info("Tworzenie uzytkownika - podano nieprawidlowy rodzaj uzytkownika")
            return Response({"message": userCreationFailed}, status=400)

        try:
            if User.objects.filter(username=data['username']).exists():
                logger.info(usernameAlreadyExists)
                return Response({"message": usernameAlreadyExists}, status=400)
            
            if User.objects.filter(email=data['email']).exists():
                logger.info(emailAlreadyExists)
                return Response({"message": emailAlreadyExists}, status=400)

            user = User.objects.create_user(username=data['username'],
                                        first_name=data['firstname'],
                                        last_name=data['lastname'],
                                        email=data['email'],
                                        password=data['password'])
            user.save()
        except Exception as e:
            logger.info("Nie udalo się utworzyć obiektu typu User " + e)
            return Response({"message": serverError}, status=500)

        try: 
            profile = Profile.objects.create(user=user, userType=userType)
            profile.save()
        except:
            logger.info("Nie udalo sie utworzyc obiektu typu Profile")
            return Response({"message": serverError}, status=500)

        logger.info(successMessage)
        return Response({"message": successMessage}, status=200)

 
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
            return Response({"message": "Nie podano parametru pk"}, status=400)

        if not Group.objects.filter(name=data['oldName'], owner=request.user).exists():
            logger.info("Grupa o nazwie " + data['oldName'] + " nie istnieje")
            return Response({"message": "Grupa ktora chcesz edytowac nie istnieje"}, status=400)
        
        if data['groupName'] != data['oldName']:
            if Group.objects.filter(name=data['groupName'], owner=request.user).exists():
                logger.info("Grupa o nazwie " + data['groupName'] + " juz istnieje")
                return Response({"message": "Juz posiadasz grupe o takiej nazwie!"}, status=400)

        try:
            groupToUpdate = Group.objects.get(name=data['oldName'], owner=request.user)            

            for userToAddToGroup in data['usersToAdd']:
                user = User.objects.get(pk=userToAddToGroup['pk'])
                groupToUpdate.users.add(user)
                createAllUserSolutionDirectory(groupToUpdate, user)
            groupToUpdate.save()

            for userToRemoveFromGroup in data['usersToRemove']:
                user = User.objects.get(pk=userToRemoveFromGroup['pk'])
                groupToUpdate.users.remove(user)
            groupToUpdate.save()           

            changeGroupSolutionDirectoryName(groupToUpdate, data['groupName']) # (obiekt Group ze stara nazwa, nowa nazwa grupy)
            groupToUpdate.name = data['groupName']
            groupToUpdate.save()

            logger.info("Grupa " + groupToUpdate.name + " zostala zaktualizowana")
        except Exception as e:
            logger.info("Nastapil blad podczas aktualizacji grupy " + data['oldName'] + " - " + str(e))
            return Response({"message": "Nastąpił błąd podczas aktualizacji grupy"}, status=500)
        
        return Response({"message": "Grupa została zaktualizowana"}, status=200)

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
        logger = logging.getLogger(__name__)
        queryset = Exercise.objects.none()
        profile = Profile.objects.get(user=self.request.user)

        logger.info("Uzytkownik " + str(self.request.user.username) + " - " + profile.userType.name + " pobiera cwiczenia")

        if profile.userType.name == "Student":
            # student nie powinien miec mozliwosci ogladania cwiczen
            # wglad do nich powinien byc jedynie poprzez Task
            queryset = Exercise.objects.none()
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
        logger = logging.getLogger(__name__)
        queryset = None
        profile = Profile.objects.get(user=self.request.user)

        logger.info("Uzytkownik " + str(self.request.user.username) + " - " + profile.userType.name + " pobiera kolokwia")

        if profile.userType.name == "Student":
            # student nie powinien miec mozliwosci ogladania kolokwium, teoretycznie
            # wglad do nich powinien byc jedynie poprzez Task
            queryset = Test.objects.none()
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
            
            if createTestRootDirectory(testToCreate):
                testToCreate.save()
            else:
                testToCreate.delete()
                logger.info("Nastąpił błąd podczas tworzenia kolokwium - nie udalo sie utworzyc katalogów")
                return Response({"message": "Nie udalo sie utworzyc kolokwium - blad tworzenia katalogow"}, status=500)

        except Exception as e:
            logger.info("Nastąpił błąd podczas tworzenia kolokwium" + str(e))
            return Response({"message": "Nastąpił błąd podczas tworzenia kolokwium"}, status=500)
        
        logger.info("Utworzono Test o pk=" + str(testToCreate.pk))
        return Response({"message": "Utworzono kolokwium"}, status=200)
    
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

            solutionType = SolutionType.objects.get(name=data['solutionType'])
            newTask.solutionType = solutionType

            newTask.save()

            newTask.assigned_to = group
            
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
        print(data['mode'])
        if data['mode'] == 'LOCK':
            # zablokowanie zadania - niemozliwe bedzie wysylanie odpowiedzi
            # zadanie oczekuje na zatwierdzenie ocen
            try:
                task_to_close = Task.objects.get(pk=data['pk'])
                task_to_close.isActive = False
                task_to_close.save()

                assigned_to = task_to_close.assigned_to
                group_members = assigned_to.users.all()
                solutions = task_to_close.solutions.all()

                for group_member in group_members:
                    intersection_qs = group_member.solutions.intersection(solutions)
                    print(intersection_qs)

                    if len(intersection_qs) == 0:
                        new_solution = Solution.objects.create(task=task_to_close, user=group_member, rate=2)
                        new_solution.save()

                logger.info("Zablokowano zadanie o pk=" + str(data['pk']))

                return Response({"message": "Zablokowano zadanie"}, status=200)
            except Exception as e:
                logger.info("Nie udalo sie zablokowac zadania o pk=" + str(data['pk']) + ". Blad=" + str(e))

                return Response({"message": "Nie udalo sie zablokowac zadania"}, status=500)

        elif data['mode'] == 'CLOSE':
            # zatwierdzenie ocen konkretnego zadania
            try:
                task_to_close = Task.objects.get(pk=data['pk'])
                
                for solution in task_to_close.solutions.all():
                    if solution.rate == None:
                        return Response({"message": "Nie mozna zamknac zadania dopoki nie wszystkie rozwiazania zostaly ocenione"}, status=400)
                    
                task_to_close.isRated = True
                task_to_close.isActive = False
                task_to_close.save()

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
        logger = logging.getLogger(__name__)
        queryset = None
        profile = Profile.objects.get(user=self.request.user)

        logger.info("Uzytkownik " + str(self.request.user.username) + " - " + profile.userType.name + " pobiera rozwiazania")

        if profile.userType.name == "Student":        
            queryset = Solution.objects.filter(user=self.request.user)
        else:
            teacher_tasks = self.request.user.my_tasks.all()
            print(teacher_tasks)
            if teacher_tasks.count() > 0:
                queryset = teacher_tasks[0].solutions.all()

                for task in teacher_tasks:
                    queryset = queryset.union(task.solutions.all())

                queryset = queryset.distinct()

        return queryset
    
    # zwroc rozwiazanie o podanym pk
    def retrieve(self, request, pk=None):
        logger = logging.getLogger(__name__)
        queryset = Solution.objects.all()
        solution = queryset.get(pk=pk)

        serializer = SolutionSerializer(solution)
        newdict = {}
        solutionValue = None

        if solution.task.taskType.name == 'Exercise':
            solution_file_path = ""

            try:
                solution_file_path = solution.solution_exercise.get().pathToFile
            except Exception as e:
                logger.info("Uzytkownik nie przyslal rozwiazania - " + str(e))
                return Response(serializer.data, status=400)

            if os.path.isfile(solution_file_path):
                with open(solution_file_path, 'r') as f:
                    solutionValue = f.read()
        else:
            solutionValue = []

            try:
                for solution_exercise in solution.solution_test.exercises_solutions.all():
                    solution_file_path = solution_exercise.pathToFile
                
                    if os.path.isfile(solution_file_path):
                        with open(solution_file_path, 'r') as f:
                            solutionValue.append(f.read())
            except Exception as e:
                logger.info("Uzytkownik nie przyslal rozwiazania - " + str(e))
                return Response(serializer.data, status=400)
                
        newdict['solutionValue'] = solutionValue

        print(newdict)
        newdict.update(serializer.data)

        return Response(newdict)
    
    # tworzenie rozwiazania i testowanie:
    # aktualne obslugiwane metody rozwiazania:
    #   - przeslanie pliku
    #   - edytor
    def create(self, request):
        # logger
        logger = logging.getLogger(self.__class__.__name__)

        data = request.data
        print(data)
        print(data['solutionType'])     
        # return Response(status=200)
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
        
        (execution_success, unit_tests_passed, message) = solExecutor.execute()

        logger.info("Wynik dzialania Executora: Wykonanie testów: " + str(execution_success) + \
                    "; Zaliczenie testow jednostkowych: " + str(unit_tests_passed) + \
                    "; Komunikat executora: " + message)

        return Response({"result": unit_tests_passed, "message": message, "test_results": solExecutor.get_result()})
    
    def update(self, request, pk=None):
        # logger
        logger = logging.getLogger(self.__class__.__name__)

        data = request.data

        if not data['mode'] == 'RATE':
            return Response({"message": "Niepoprawny typ operacji"}, status=400)
        
        final_rate = 0
        
        try:
            with transaction.atomic():
                solution_to_rate = Solution.objects.get(pk=data['pk'])
                for exercise_rate in data['solRates']:
                    solution_exercise = SolutionExercise.objects.get(pk=exercise_rate['pk'])
                    solution_exercise.rate = float(exercise_rate['rate'])
                    final_rate += float(exercise_rate['rate'])
                    solution_exercise.save()

                    logger.info("Ustawiono pole rate=" + str(exercise_rate['rate']) + " obiektu SolutionExericse pk=" + str(exercise_rate['pk']))
            
                if solution_to_rate.task.taskType.name == 'Test':
                    final_rate = final_rate / len(data['solRates'])
                    final_rate = round(final_rate * 2) / 2
                    solution_to_rate.rate = final_rate
                    solution_to_rate.solution_test.rate = final_rate
                else:
                    solution_to_rate.rate = final_rate
                
                solution_to_rate.save()
        except Exception as e:
            logger.info("Wystapil blad podczas zapisywania ocen - " + str(e))
            print(e)
            return Response({"message": "Wystapil blad podczas zapisywania ocen"}, status=500)
        
        return Response({"message": "Zadanie zostalo ocenione"}, status=200) 

# Klasa obslugujaca resetowanie hasla
class ResetPasswordHashView(APIView):
    def get(self, request, hash_string=None):
        # logger        
        logger = logging.getLogger(self.__class__.__name__)
        logger.info("Proba zresetowania hasla studenta dla hash=" + str(hash_string))

        does_hash_exist = False
        response_message = ""

        try:
            if not ResetPasswordHash.objects.filter(hash_value=hash_string).exists():
                does_hash_exist = False
                response_message = "Link nie istnieje"
                logger.info(response_message)
                return Response({"value": does_hash_exist, "message": response_message}, status=400)    
                
            registration_hash = ResetPasswordHash.objects.get(hash_value=hash_string)
            
            if registration_hash.consumed:
                does_hash_exist = True
                response_message = "Link zostal juz wykorzystany"
                logger.info(response_message)
                return Response({"value": does_hash_exist, "message": response_message}, status=406)
            
            does_hash_exist = True
            response_message = "Podaj nowe haslo"
            logger.info("Podano poprawny link resetowania hasla.")
            return Response({"value": does_hash_exist, "message": response_message, "email": registration_hash.owner.email}, status=200)
        except Exception as e:
            logger.info(str(e))
            return Response({"value": False, "message": "Wystapil nieoczekiwany blad po stronie serwera"}, status=500)

    # metoda obsluguje utworzenie obiektu ResetPasswordHash z wykorzystaniem
    # klasy 'django.core.signing.Signer'
    def post(self, request, hash_string=None):
        # logger        
        logger = logging.getLogger(self.__class__.__name__)
        data = request.data
        print(data)
        if 'email' not in data:
            return Response({"message": "Nie podano adresu email"}, status=400)

        email_address = data['email']
        logger.info("Utworzenie linku resetujacego haslo dla adresu email=" + str(email_address))
        
        if not User.objects.filter(email=email_address).exists():
            response_message = "W serwisie nie ma uzytkownika zarejestrowanego na ten adres email " 
            logger.info(response_message + str(email_address))
            return Response({"message": response_message}, status=400)
        
        user = User.objects.get(email=email_address)
        time_salt = str(time.time())
        signer = Signer(salt=time_salt)
        hash_sign = signer.sign(user.email)
        hash_value = hash_sign.split(":")[1]

        reset_pass_hash, created = ResetPasswordHash.objects.get_or_create(owner=user)
        reset_pass_hash.hash_value = hash_value
        reset_pass_hash.consumed= False
        
        # wyslanie maila
        email_service = EmailService()
        send_result = email_service.send_reset_password_link(email_address, hash_value)
        
        try:
            result_message = ""
            result_status = 200

            if send_result:
                reset_pass_hash.save()
                result_message = "Mail z linkiem do zresetowania hasla zostal wyslany."
                logger.info(result_message)
            else:
                reset_pass_hash.delete()
                result_message = "Nie udalo sie wyslac maila z linkiem do zresetowania hasla. "
                result_status = 500
                logger.info(result_message + ". Obiekt RegistrationHash zostaje usuniety.")

            return Response({"message": result_message, "value": send_result}, status=result_status)
        except Exception as e:
            logger.info(str(e))
            return Response({"message": "Nastapil blad po stronie serwera."}, status=500)


    # metoda przyjmuje dane - hash? i nowe haslo i zapisuje zmiany  
    def put(self, request, hash_string=None):
        # logger        
        logger = logging.getLogger(self.__class__.__name__)
        data = request.data

        reset_password_hash = None

        if not ResetPasswordHash.objects.filter(hash_value=hash_string).exists():
            return Response({"message": "Link nie istnieje"}, status=400)

        reset_password_hash = ResetPasswordHash.objects.get(hash_value=hash_string)

        if reset_password_hash.consumed:
            return Response({"message": "Link nie aktywny"}, status=406)
        
        data = request.data

        if 'password' not in data or 'passwordRepeat' not in data:
            return Response({"message": "Nie podano wszystkich danych"}, status=400)

        if data['password'] != data['passwordRepeat']:
            return Response({"message": "Podano rozne hasla"}, status=400)

        try:
            with transaction.atomic():
                user_to_password_change = reset_password_hash.owner
                user_to_password_change.set_password(data['password'])
                reset_password_hash.consumed = True
                reset_password_hash.save()
                user_to_password_change.save()
            logger.info("Haslo uzytkownika zarejestrowanego na adres " + user_to_password_change.email + " zostalo zmienione")
            return Response({"message": "Haslo zostalo zmienione pomyslnie"}, status=200)
        except Exception as e:
            logger.info(str(e))
            return Response({"message": "Nastapil nieoczekiwany blad po stronie serwera"}, status=500)