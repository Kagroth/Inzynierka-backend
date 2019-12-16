
from . import views
from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('students', views.StudentViewSet, basename="Students")
router.register('groups', views.GroupViewSet, basename="Groups")
router.register('exercises', views.ExerciseViewSet, basename="Exercises")
router.register('tests', views.TestViewSet, basename="Tests")
router.register('tasks', views.TaskViewSet, basename="Tasks")
router.register('solutions', views.SolutionViewSet, basename="Solutions")

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_obtain_refresh'),
    path('profile/<str:username>', views.ProfileView.as_view()),
    path('levels/', views.LevelView.as_view()),
    path('languages/', views.LanguageView.as_view()),
    path('solution_types/', views.SolutionTypeView.as_view()),
    path('', include(router.urls)),
    #path('users/', views.ListUsers.as_view()),
    #path('groups/', views.ListGroup.as_view()),
]
