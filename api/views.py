from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Appointment, HealthProfessional
from .serializers import AppointmentSerializer, HealthProfessionalSerializer
from .services import AsaasService


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
    filterset_fields = ["health_professional"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        appointment_id = serializer.data.get("id")
        billing_info = AsaasService.generate_mock_billing(appointment_id)

        response_data = serializer.data
        response_data["payment_link"] = billing_info.get("payment_url")

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
