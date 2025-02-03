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

# ClientOption Serializer (for custom description)
class ClientOptionSerializer(serializers.ModelSerializer):
    option_id = serializers.IntegerField()  # To pass option ID in the request

    class Meta:
        model = ClientOption
        fields = ['option_id', 'custom_description']

# ClientResponse Serializer (handles multiple options)
class ClientResponseSerializer(serializers.ModelSerializer):
    field_id = serializers.IntegerField()  # To pass field ID
    options = ClientOptionSerializer(many=True)  # Nested options

    class Meta:
        model = ClientResponse
        fields = ['field_id', 'options']

# ClientSubmission Serializer
class ClientSubmissionSerializer(serializers.ModelSerializer):
    responses = ClientResponseSerializer(many=True)
    client_name = serializers.CharField()

    class Meta:
        model = ClientSubmission
        fields = ['client_name', 'responses']

    # Custom create logic
    def create(self, validated_data):
        client_name = validated_data['client_name']
        responses_data = validated_data['responses']

        # Create Client Submission
        submission = ClientSubmission.objects.create(client_name=client_name)

        # Loop through responses
        for response_data in responses_data:
            field = Field.objects.get(id=response_data['field_id'])
            response = ClientResponse.objects.create(submission=submission, field=field)

            # Handle selected options
            for option_data in response_data['options']:
                option = Option.objects.get(id=option_data['option_id'])
                ClientOption.objects.create(
                    response=response,
                    option=option,
                    custom_description=option_data.get('custom_description', option.description)
                )

        return submission



