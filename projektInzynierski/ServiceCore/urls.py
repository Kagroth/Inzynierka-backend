
from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('users/', views.ListUsers.as_view()),
    path('groups/', views.ListGroup.as_view()),
]
