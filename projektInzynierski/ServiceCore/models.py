from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserType(models.Model):
    name = models.CharField(max_length=32)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    userType = models.ForeignKey(UserType, on_delete=models.CASCADE)

class Exercise(models.Model):
    title = models.CharField(max_length=128)
    language = models.CharField(max_length=32)
    Content = models.TextField()
    Level = models.IntegerField()

class UnitTest(models.Model):
    pathToFile = models.FilePathField()
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

class Test(models.Model):
    name = models.CharField(max_length=32)
    exercises = models.ManyToManyField(Exercise)

class TaskType(models.Model):
    name = models.CharField(max_length=32)

class Task(models.Model):
    taskType = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

class Group(models.Model):
    name = models.CharField(max_length=32)
    users = models.ManyToManyField(User)
    tasks = models.ManyToManyField(Task)

class Solution(models.Model):
    pathToFile = models.FilePathField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.IntegerField()




