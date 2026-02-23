import re
from rest_framework import serializers
from .models import HealthProfessional, Appointment

class HealthProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfessional
        fields = ['id', 'social_name', 'profession', 'address', 'contact', 'is_active']
        read_only_fields = ['id']
    
    def validate_social_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Social name cannot be empty.")
        return value
    
    def validate_contact(self, value):
        clean_contact = re.sub(r'[^0-9]', '', value)

        if len(clean_contact) not in (10,11):
            raise serializers.ValidationError("Contact number must be in a valid Brazilian phone format (11 digits including area code).")
        return value

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'professional', 'appointment_date']
        read_only_fields = ['id']