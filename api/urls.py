from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, HealthProfessionalViewSet

router = DefaultRouter()
router.register(r'professionals', HealthProfessionalViewSet, basename='professional')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
]
