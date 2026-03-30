from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'conda-environments', views.CondaEnvironmentViewSet, basename='condaenvironment')
