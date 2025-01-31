from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company, CompanyStaff

class CompanySerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    
    def validate_password(self, value):
        # need to add password validation as per requirement
        return value

class CompanyStaffSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
