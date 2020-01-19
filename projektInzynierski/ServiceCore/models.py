from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=32)
    allowed_extension = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return self.name + " - " + self.allowed_extension


class Level(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class UserType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class SolutionType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

'''
    User model posiada pola:
        first_name, last_name, username, email, password
'''
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    userType = models.ForeignKey(UserType, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.userType.name

# Klasa reprezentuje pojedyncze cwiczenie. Sklada sie z:
#   - autora
#   - tytulu
#   - języka programowania
#   - tresci cwiczenia
#   - poziomu zaawansowania
class Exercise(models.Model):
    author = models.ForeignKey(User, related_name="exercises", blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    language = models.ForeignKey(Language, related_name="language", blank=True, null=True, on_delete=models.CASCADE)
    content = models.TextField()
    level = models.ForeignKey(Level, related_name="level", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + " - " + self.language.name + " - " + self.author.username


# Klasa reprezentuje test jednostkowy przypisany do konkretnego cwiczenia
#   - pathTofile - sciezka do pliku w ktorym zapisany jest test
#   - exercise - zadanie z ktorym test jest powiazany
class UnitTest(models.Model):
    pathToFile = models.FilePathField(max_length=1024)
    exercise = models.ForeignKey(Exercise, related_name="unit_tests", on_delete=models.CASCADE)
    content = models.CharField(max_length=2048, blank=True, null=True)

# Klasa reprezentuje kolokwium, ktore sklada sie z kilku cwiczen
#   - title - nazwa kolokwium
#   - exercises - cwiczenia tworzace kolokwium 
class Test(models.Model):
    author = models.ForeignKey(User, related_name="tests", blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=32)
    exercises = models.ManyToManyField(Exercise, related_name="exercises")

    def __str__(self):
        return self.title + " - " + self.author.username

# Klasa reprezentuje rodzaj zadania (jest tylko Test lub Exercise)
#   - name - nazwa rodzaju zadania 
class TaskType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

# Klasa reprezentuje zadanie ktore mozna przydzielac studentom.
#   - author - autor zadania
#   - taskType - rodzaj zadania (Test/kolokwium lub Exercise/cwiczenie)
#   - title - tytul zadania
#   - exercise - klucz powaizany z obiektem typu Exercise (zalezne od taskType)
#   - test - klucz powiazany z obiektem typu Test (zalezne od taskType)
#   - isActive - czy jest aktywny
#   - created_at - data utworzenia zadania
class Task(models.Model):
    author = models.ForeignKey(User, related_name="my_tasks", blank=True, null=True, on_delete=models.CASCADE)
    taskType = models.ForeignKey(TaskType, null=True, on_delete=models.CASCADE)
    solutionType = models.ForeignKey(SolutionType, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, blank=True, null=True)
    exercise = models.ForeignKey(Exercise, null=True, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, blank=True, null=True, on_delete=models.CASCADE)
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username + " - " + self.taskType.name + " - " + self.title


# Klasa reprezentuje grupe skladajaca sie z uzytkownikow (studentow)
#   - name - nazwa grupy
#   - owner - wlasciciel grupy
#   - users - uzytkownicy
#   - tasks - zadania przypisane konkretnej grupie
class Group(models.Model):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey(User, related_name="group", blank=True, null=True, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name="membershipGroups", blank=True)
    tasks = models.ManyToManyField(Task, related_name="assignedTo", blank=True)

    def __str__(self):
        return self.name

# Klasa reprezentuje rozwiazanie nadeslane przez uzytkownika
#   - pathToFile - sciezka do pliku z rozwiazaniem
#   - task - zadanie ktorego tyczy sie rozwiazanie
#   - user - autor rozwiazania
#   - rate - ocena rozwaizania
class Solution(models.Model):
    task = models.ForeignKey(Task, related_name="solutions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="solutions", on_delete=models.CASCADE)
    rate = models.FloatField(blank=True, null=True)  

class SolutionTest(models.Model):
    solution = models.OneToOneField(Solution, related_name="solution_test", on_delete=models.CASCADE)    
    rate = models.FloatField(blank=True, null=True)

class SolutionExercise(models.Model):
    solution = models.ForeignKey(Solution, related_name="solution_exercise", on_delete=models.CASCADE)
    test = models.ForeignKey(SolutionTest, related_name="exercises_solutions", blank=True, null=True, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise,  blank=True, null=True, on_delete=models.CASCADE)
    pathToFile = models.FilePathField(max_length=1024)
    rate = models.FloatField(blank=True, null=True)
    github_link = models.CharField(max_length=4096, blank=True, null=True)
