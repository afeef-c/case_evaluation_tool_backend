from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company, Field,Option, ClientOption,EvaluationRule,EvaluationOutcome, ClientResponse,ClientSubmission,EvaluationRuleCondition

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


class FieldSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Field
        fields = ['id', 'name', 'company','options']


class EvaluationOutcomeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EvaluationOutcome
        fields = ['company','name','description']




class EvaluationRuleSerializer(serializers.ModelSerializer):
    outcome = EvaluationOutcomeSerializer()

    class Meta:
        model = EvaluationRule
        fields = ['id','company','outcome']


class EvaluationRuleConditionSerialixer(serializers.ModelSerializer):
    option = OptionSerializer(many=True)
    rule = EvaluationRuleSerializer()
    class Meta:
        model = EvaluationRuleCondition
        fields = [ 'rule', 'option']



class ClientOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientOption
        fields = ['id', 'option', 'custom_description']

class ClientResponseSerializer(serializers.ModelSerializer):
    client_options = ClientOptionSerializer(many=True)

    class Meta:
        model = ClientResponse
        fields = ['id', 'client_options']

    def create(self, validated_data):
        client_options_data = validated_data.pop('client_options')
        response = ClientResponse.objects.create(**validated_data)

        for option_data in client_options_data:
            ClientOption.objects.create(response=response, **option_data)

        return response

class ClientSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSubmission
        fields = ['id', 'client_name', 'client_email', 'client_phone', 'company', 'is_submitted', 'pdf_file']

