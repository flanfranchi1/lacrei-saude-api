from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HealthProfessionalViewSet, AppointmentViewSet

router = DefaultRouter()
router.register(r'professionals', HealthProfessionalViewSet, basename='professional')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]