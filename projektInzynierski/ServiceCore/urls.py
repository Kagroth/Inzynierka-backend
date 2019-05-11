
from . import views
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_obtain_pair'),
    path('', include(router.urls)),
    #path('users/', views.ListUsers.as_view()),
    #path('groups/', views.ListGroup.as_view()),
]
