
from . import views
from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_obtain_pair'),
    path('', views.index),
    path('users/', views.ListUsers.as_view()),
    path('groups/', views.ListGroup.as_view()),
]
