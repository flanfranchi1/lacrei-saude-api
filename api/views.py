from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Appointment, HealthProfessional
from .serializers import AppointmentSerializer, HealthProfessionalSerializer


class HealthProfessionalViewSet(viewsets.ModelViewSet):
    queryset = HealthProfessional.objects.all()
    serializer_class = HealthProfessionalSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_prolds = ['health_professional']
