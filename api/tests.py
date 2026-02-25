from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Appointment, HealthProfessional


class HealthProfessionalTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testadmin", password="testpassword"
        )
        url_token = reverse("token_obtain_pair")
        response = self.client.post(
            url_token,
            {"username": "testadmin", "password": "testpassword"},
            format="json",
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.professional = HealthProfessional.objects.create(
            social_name="Dra. Teste Base",
            profession="Doctor",
            address="Rua Base, 0",
            contact="11888888888",
        )

    def test_create_professional_success(self):

        payload = {
            "social_name": "Dr. Fernando",
            "profession": "Doctor",
            "address": "Rua das Flores, 123",
            "contact": "11987654321",
        }
        url = reverse("professional-list")
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_professional_unauthenticated_blocks_access(self):
        self.client.credentials()
        url = reverse("professional-list")
        response = self.client.post(url, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_professional_invalid_data(self):
        payload = {"social_name": "Dr. 123", "contact": "abc"}
        url = reverse("professional-list")
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_professionals(self):
        url = reverse("professional-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_professional(self):

        url = reverse("professional-detail", args=[self.professional.id])
        payload = {
            "social_name": "Dra. Teste Editado",
            "profession": "Doctor",
            "address": "Rua Nova, 10",
            "contact": "11888888888",
            "is_active": True,
        }
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.professional.refresh_from_db()
        self.assertEqual(self.professional.social_name, "Dra. Teste Editado")

    def test_soft_delete_professional(self):
        url = reverse("professional-detail", args=[self.professional.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.professional.refresh_from_db()
        self.assertFalse(self.professional.is_active)


class AppointmentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testadmin2", password="testpassword"
        )
        url_token = reverse("token_obtain_pair")
        response = self.client.post(
            url_token,
            {"username": "testadmin2", "password": "testpassword"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

        self.health_professional = HealthProfessional.objects.create(
            social_name="Dr. Consulta",
            profession="medico",
            address="Rua Clinica, 1",
            contact="11999999999",
        )

        self.future_date = timezone.now() + timedelta(days=1)
        self.appointment = Appointment.objects.create(
            health_professional=self.health_professional,  # AJUSTADO AQUI
            appointment_date=self.future_date,
        )

    def test_create_appointment_success(self):
        url = reverse("appointment-list")
        payload = {
            "health_professional": str(
                self.health_professional.id
            ),  # AJUSTADO AQUI NO JSON
            "appointment_date": (timezone.now() + timedelta(days=2)).isoformat(),
        }
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)

    def test_filter_appointments_by_professional(self):
        url = reverse("appointment-list")

        response = self.client.get(
            f"{url}?health_professional={self.health_professional.id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_delete_appointment(self):
        url = reverse("appointment-detail", args=[self.appointment.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)
