from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company,CompanyStaff, Field,Option,EvaluationRule,EvaluationOutcome,EvaluationRuleCondition


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','password']

class CompanyStaffSerializer_(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = CompanyStaff
        fields = ['id', 'user']

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




# class CompanySerializer(serializers.ModelSerializer):
#     admins = CompanyAdminSerializer(many=True)  
#     staffs = CompanyAdminSerializer(many=True)
#     class Meta:
#         model = Company
#         fields = ['id','name', 'admins', 'staffs']





class CompanyStaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CompanyStaff
        fields = ['id', 'name', 'username', 'password']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        # Check if the user exists
        user, created = User.objects.get_or_create(username=username)

        if not created:
            # If user exists, update the password
            user.set_password(password)
            user.save()
        else:
            # If new user, set password properly
            user.set_password(password)
            user.save()

        # Ensure CompanyStaff entry exists
        staff, staff_created = CompanyStaff.objects.get_or_create(user=user, defaults=validated_data)

        if not staff_created:
            # If staff already exists, update fields
            for key, value in validated_data.items():
                setattr(staff, key, value)
            staff.save()

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




