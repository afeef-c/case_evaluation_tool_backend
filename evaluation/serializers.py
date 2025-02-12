from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company,CompanyStaff, Field,Option,EvaluationRule,EvaluationOutcome,EvaluationRuleCondition,ClientSubmission,ClientSubmissionOption


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']

class CompanyStaffSerializer_(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")  # Get username from related user model
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = CompanyStaff
        fields = ['id','name', 'username', 'password']

class CompanyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'password']
        extra_kwargs = {'password': {'write_only': True}}


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)  # Admin's name (used for user creation)
    username = serializers.CharField(write_only=True)  # Admin's username
    password = serializers.CharField(write_only=True)  # Admin's password
    admin = serializers.SerializerMethodField()  # Read-only field for response

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'name', 'username', 'password', 'admin']

    def get_admin(self, obj):
        """Return admin user details"""
        if obj.admin:
            return {
                "id": obj.admin.id,
                "username": obj.admin.username,
            }
        return None


class CompanyDataSerializer(serializers.ModelSerializer):
    admin = CompanyAdminSerializer()
    staff = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = ['id', 'company_name','name', 'admin', 'staff']

    def get_staff(self, obj):
        staffs = CompanyStaff.objects.filter(company=obj)
        return CompanyStaffSerializer_(staffs, many=True).data






class CompanyStaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = CompanyStaff
        fields = ['id', 'name', 'username', 'password']



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


class EvaluationRuleConditionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(many=True)
    rule = EvaluationRuleSerializer()
    class Meta:
        model = EvaluationRuleCondition
        fields = [ 'rule', 'option']

class ClientSubmissionOptionSerializer(serializers.ModelSerializer):
    option = OptionSerializer(read_only=True)  # Fetch option details
    option_id = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(), source='option', write_only=True
    )

    class Meta:
        model = ClientSubmissionOption
        fields = ['id', 'submission', 'option', 'option_id', 'updated_description']


class ClientSubmissionSerializer(serializers.ModelSerializer):
    selected_options = ClientSubmissionOptionSerializer(many=True, source='submission_options', read_only=True)
    generated_outcome = serializers.PrimaryKeyRelatedField(queryset=EvaluationOutcome.objects.all())

    class Meta:
        model = ClientSubmission
        fields = [
            'id', 'client_name', 'client_email', 'client_phone',
            'generated_outcome', 'updated_out_description', 'company',
            'submitted_by', 'selected_options'
        ]

