from django.contrib import admin
from ServiceCore.models import *

# Register your models here.
# Modele w panelu administratora
admin.site.register(UserType)
admin.site.register(Language)
admin.site.register(Level)
admin.site.register(Profile)
admin.site.register(Exercise)
admin.site.register(UnitTest)
admin.site.register(Test)
admin.site.register(TaskType)
admin.site.register(Task)
admin.site.register(Group)
admin.site.register(Solution)
admin.site.register(SolutionType)