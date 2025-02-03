from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company, Field,Option, ClientOption, ClientResponse,ClientSubmission

class CompanySerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    
    def validate_password(self, value):
        # need to add password validation as per requirement
        return value


class CompanyStaffSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)



class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'field', 'value', 'description']


class ClientOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientOption
        fields = ['id', 'option', 'custom_description']

class ClientResponseSerializer(serializers.ModelSerializer):
    client_options = ClientOptionSerializer(many=True)

    class Meta:
        model = ClientResponse
        fields = ['id', 'submission', 'client_options']

    def create(self, validated_data):
        client_options_data = validated_data.pop('client_options')
        response = ClientResponse.objects.create(**validated_data)

        for option_data in client_options_data:
            ClientOption.objects.create(response=response, **option_data)

        return response

class ClientSubmissionSerializer(serializers.ModelSerializer):
    responses = ClientResponseSerializer(many=True, required=False)

    class Meta:
        model = ClientSubmission
        fields = ['id', 'client_name', 'client_email', 'client_phone', 'company', 'is_submitted', 'responses']


