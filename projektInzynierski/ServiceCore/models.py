from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserType(models.Model):
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

class Exercise(models.Model):
    author = models.ForeignKey(User, related_name="exercises", blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    language = models.CharField(max_length=32)
    content = models.TextField()
    level = models.IntegerField()

    def __str__(self):
        return self.title + " - " + self.language + " - " + self.author.username

class UnitTest(models.Model):
    pathToFile = models.FilePathField()
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

class Test(models.Model):
    name = models.CharField(max_length=32)
    exercises = models.ManyToManyField(Exercise)

class TaskType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

class Task(models.Model):
    author = models.ForeignKey(User, related_name="my_tasks", blank=True, null=True, on_delete=models.CASCADE)
    taskType = models.ForeignKey(TaskType, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, blank=True, null=True)
    exercise = models.ForeignKey(Exercise, null=True, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, blank=True, null=True, on_delete=models.CASCADE)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.author.username + " - " + self.taskType.name

class Group(models.Model):
    name = models.CharField(max_length=32)
    owner = models.ForeignKey(User, related_name="group", blank=True, null=True, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name="membershipGroups", blank=True)
    tasks = models.ManyToManyField(Task, related_name="tasks", blank=True)

    def __str__(self):
        return self.name

class Solution(models.Model):
    pathToFile = models.FilePathField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.IntegerField()




