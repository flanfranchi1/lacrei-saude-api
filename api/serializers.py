from rest_framework import serializers
from .models import HealthProfessional, Appointment

class HealthProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfessional
        fields = ['id', 'social_name', 'profession', 'address', 'contact', 'is_active']
        read_only_fields = ['id']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'professional', 'appointment_date']
        read_only_fields = ['id']