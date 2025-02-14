from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Company,CompanyStaff,CompanyData, Field,Option,EvaluationRule,EvaluationOutcome,EvaluationRuleCondition,ClientSubmission,ClientSubmissionOption
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if user.is_superuser:
            role = "Agency Admin"
        elif user.is_staff and hasattr(user, 'company'):
            role = "Company Admin"
        elif hasattr(user, 'staff_profile'):
            role = "Company Staff"
        else:
            role = None

        # Add custom claims
        token['username'] = user.username
        token['role'] = role  

        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Extract user ID from the refresh token
        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh.payload.get("user_id")

        # Fetch user from database
        user = User.objects.filter(id=user_id).first()

        if not user:
            raise serializers.ValidationError("Invalid token: user does not exist")

        # Create a new customized access token
        access = AccessToken.for_user(user)
        access["username"] = user.username

        # Assign role based on user type
        if user.is_superuser:
            access["role"] = "Agency Admin"
        elif user.is_staff and hasattr(user, "company"):
            access["role"] = "Company Admin"
        elif hasattr(user, "staff_profile"):
            access["role"] = "Company Staff"
        else:
            access["role"] = None

        # Replace the default access token with the customized one
        data["access"] = str(access)
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']


class CompanyDataSerializer_(serializers.ModelSerializer):
    class Meta:
        model = CompanyData
        fields = ['id', 'logo_img', 'color', 'footer_email', 'footer_phone', 'company']  # Ensure these fields exist
        extra_kwargs = {'company': {'read_only': True}}  # Prevent manual input of `company`


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
        fields = ['id', 'value', 'description']


class FieldSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Field
        fields = ['id', 'name', 'company','options']


class EvaluationOutcomeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EvaluationOutcome
        fields = ['id','company','name','description']




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
        fields = ['id', 'option', 'option_id', 'updated_description']


class ClientSubmissionSerializer(serializers.ModelSerializer):
    selected_options = ClientSubmissionOptionSerializer(many=True, source='submission_options', read_only=True)
    generated_outcome = serializers.PrimaryKeyRelatedField(queryset=EvaluationOutcome.objects.all())
    
    class Meta:
        model = ClientSubmission
        fields = [
            'id', 'client_name', 'client_email', 'client_phone',
            'generated_outcome','pdf_file', 'updated_out_description', 'company',
            'submitted_by', 'selected_options'
        ]

