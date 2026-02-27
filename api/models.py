import uuid

from django.db import models


class HealthProfessional(models.Model):
    class ProfessionChoices(models.TextChoices):
        DOCTOR = "Doctor", "Médico(a)"
        NURSE = "Nurse", "Enfermeiro(a)"
        PSYCHOLOGIST = "psychologist", "Psicólogo(a)"
        PHYSIOTHERAPIST = "physiotherapist", "Fisioterapeuta"
        NUTRITIONIST = "nutritionist", "Nutricionista"
        OTHER = "other", "Outro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    social_name = models.CharField(max_length=255)
    profession = models.CharField(
        max_length=20,
        choices=ProfessionChoices.choices,
        default=ProfessionChoices.OTHER,
    )
    address = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    health_professional = models.ForeignKey(HealthProfessional, on_delete=models.PROTECT, related_name="appointments")
    appointment_date = models.DateTimeField()

    def __str__(self):
        return f"Appointment with {self.health_professional.social_name} on {self.appointment_date}"
