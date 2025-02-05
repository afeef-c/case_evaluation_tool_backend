from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company,CompanyStaff, Field,Option,EvaluationRule,EvaluationOutcome,EvaluationRuleCondition


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','password']

class CompanyStaffSerializer_(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CompanyStaff
        fields = ['id', 'name', 'user', 'password']

class CompanySerializer(serializers.ModelSerializer):
    admins = UserSerializer(many=True)
    staff = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'admins', 'staff']

    def get_staff(self, obj):
        staffs = CompanyStaff.objects.filter(company=obj)
        return CompanyStaffSerializer_(staffs, many=True).data


class CompanyAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'password']
        extra_kwargs = {'password': {'write_only': True}}



# class CompanySerializer(serializers.ModelSerializer):
#     admins = CompanyAdminSerializer(many=True)  
#     staffs = CompanyAdminSerializer(many=True)
#     class Meta:
#         model = Company
#         fields = ['id','name', 'admins', 'staffs']




class CompanyStaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CompanyStaff
        fields = ['id', 'name', 'username', 'password']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        user = User.objects.create_user(username=username, password=password)
        staff = CompanyStaff.objects.create(user=user, **validated_data)
        return staff


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




