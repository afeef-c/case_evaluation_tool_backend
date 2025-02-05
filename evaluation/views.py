from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAgencyAdmin, IsCompanyAdmin,IsCompanyAdminOrStaff
from .serializers import CompanySerializer,CompanyAdminSerializer, CompanyStaffSerializer,FieldSerializer,EvaluationRuleConditionSerialixer
from django.contrib.auth.models import User
from .models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions


# Create your views here.
class Login(APIView):
    
    def post(self, request):
        
        try:
            data=request.data
            username=data['username']
            password=data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                

                    login(request, user)
                    token = RefreshToken.for_user(user)
                    if user.is_superuser:
                        role = "Agency Admin"
                    elif user.is_staff and hasattr(user, 'company'):
                        role = "Company Admin"
                    elif hasattr(user, 'staff_profile'):
                        role = "Company Staff"
                    else:
                        role = None
                        
                    
                    # add role in response
                    return Response({
                        'message': 'You are successfully logged in.',
                        'refresh': str(token),
                        'access': str(token.access_token),
                        'username': user.username,
                        'role' : role
                        
                    },status=200)
            else:
                return Response({
                    'message': 'Invalid username or password.'
                }, status=404)

        except Exception as e:
            return Response({
                    'error': str(e)+' missing' ,
                    'message':"Incomplete request data"
                            },status=400)
        

# add Company and Admin by superAdmin
class CompanyCreateAPIView(APIView):
    permission_classes = [IsAgencyAdmin]

    def post(self, request):
        serializer = CompanySerializer(data=request.data)

        if serializer.is_valid():
            company_data = serializer.validated_data
            admins_data = company_data.pop('admins')

            # Create Company
            company = Company.objects.create(**company_data)

            # Create Admins with is_staff=True
            for admin_data in admins_data:
                admin_serializer = CompanyAdminSerializer(data=admin_data)
                if admin_serializer.is_valid():
                    admin_validated_data = admin_serializer.validated_data
                    
                    # Ensure is_staff is set to True
                    admin = User.objects.create_user(**admin_validated_data, is_staff=True)
                    
                    # Add admin to the company
                    company.admins.add(admin)
                else:
                    return Response(admin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(CompanySerializer(company).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# add Admin for existing  Company
class AddAdminAPIView(APIView):
    permission_classes = [IsAgencyAdmin]
    
    def post(self, request, company_id):
        company = get_object_or_404(Company, id=company_id)
        admin_serializer = CompanyAdminSerializer(data=request.data)
        
        if admin_serializer.is_valid():
            admin = User.objects.create_user(**admin_serializer.validated_data)
            company.admins.add(admin)
            return Response({"message": "Admin added successfully"}, status=status.HTTP_201_CREATED)

        return Response(admin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Remove Admin from a Company
class RemoveAdminAPIView(APIView):
    permission_classes = [IsAgencyAdmin]
    
    def delete(self, request, company_id, admin_id):
        company = get_object_or_404(Company, id=company_id)
        admin = get_object_or_404(User, id=admin_id)

        if admin in company.admins.all():
            company.admins.remove(admin)
            admin.delete()  # Optional: Delete the user entirely or just remove the relation
            return Response({"message": "Admin removed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Admin not associated with this company"}, status=status.HTTP_400_BAD_REQUEST)




class AddCompanyStaffAPIView(APIView):
    permission_classes = [IsCompanyAdmin]

    def post(self, request):
        try:
            # Automatically get the company associated with the logged-in admin
            company = Company.objects.get(admins=request.user)
        except Company.DoesNotExist:
            return Response({"error": "You are not authorized to add staff."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CompanyStaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=company)
            return Response({"message": "Staff added successfully!", "staff": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddFieldsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]
    def post(self, request):
        try:
            data = request.data

            # company = Company.objects.get(admin_id=data.get('userId'))
            company = Company.objects.get(admins=request.user)
            

            for field_data in data.get('field_options', []):
                field = Field.objects.create(company=company, name=field_data['name'])
                for option_data in field_data.get('options', []):
                    Option.objects.create(field=field, value=option_data['name'], description=option_data['description'])

            for eval_option in data.get('case_evaluation_options', []):
                EvaluationOutcome.objects.create(company=company, name=eval_option['name'], description=eval_option['description'])

            return Response({"message": "Fields and options added successfully."}, status=201)
        except Exception as e:
             return Response(
                {"error": str(e)},
                status=500
            )
    

class FieldListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsCompanyAdmin]

    def get(self, request):
        fields = Field.objects.all()
        serializer = FieldSerializer(fields, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddRulesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]

    
    def post(self, request):
        try:
            data = request.data

            # Ensure required fields exist
            required_fields = [ 'field_options', 'case_evaluation']
            if not all(field in data for field in required_fields):
                return Response({"error": "Required fields are missing."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            
            try:
                # Check if the user is an admin of any company
                company = Company.objects.filter(admins=user).first()
                
            except CompanyStaff.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)


            try:
                evaluation_outcome = EvaluationOutcome.objects.get(company=company, name=data['case_evaluation'])
            except EvaluationOutcome.DoesNotExist:
                return Response({"error": "Evaluation outcome not found."}, status=status.HTTP_404_NOT_FOUND)

            # Create rule
            rule = EvaluationRule.objects.create(company=company, outcome=evaluation_outcome)

            # Collect options
            options = []
            for field_option in data.get('field_options', []):
                option_name = field_option.get("option")
                field = Field.objects.get(name=field_option.get("name"))
                
                try:
                    
                    option = Option.objects.get(field =field ,value=option_name)
                    options.append(option)
                except Option.DoesNotExist:
                    return Response({"error": f"Option '{option_name}' not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if a rule condition with the same set of options exists
            existing_conditions = EvaluationRuleCondition.objects.filter(rule__company=company)
            
            for condition in existing_conditions:
                
                if set(condition.option.all()) == set(options):
                    return Response({'error': 'Rule condition with the same set of options already exists'}, status=status.HTTP_400_BAD_REQUEST)

            # Create rule condition
            rule_condition = EvaluationRuleCondition.objects.create(rule=rule)
            rule_condition.option.set(options)
            rule_condition.save()

            return Response({'message': 'Rule conditions added successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListRulesView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsCompanyAdmin]


    def get(self, request):
        rules = EvaluationRuleCondition.objects.all()
        serializer = EvaluationRuleConditionSerialixer(rules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UpdateRuleView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]

    def patch(self, request, rule_id):
        try:
            data = request.data

            try:
                rule = EvaluationRule.objects.get(id=rule_id)
            except EvaluationRule.DoesNotExist:
                return Response({"error": "Rule not found."}, status=status.HTTP_404_NOT_FOUND)

            options = []
            for field_option in data.get('field_options', []):
                option_name = field_option.get("option")
                field = Field.objects.get(name=field_option.get("name"))

                try:
                    option = Option.objects.get(field=field, value=option_name)
                    options.append(option)
                except Option.DoesNotExist:
                    return Response({"error": f"Option '{option_name}' not found."}, status=status.HTTP_404_NOT_FOUND)

            rule_condition = EvaluationRuleCondition.objects.filter(rule=rule).first()
            if rule_condition:
                rule_condition.option.set(options)
                rule_condition.save()

            return Response({'message': 'Rule updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteRuleView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]

    def delete(self, request, rule_id):
        try:
            try:
                rule = EvaluationRule.objects.get(id=rule_id)
            except EvaluationRule.DoesNotExist:
                return Response({"error": "Rule not found."}, status=status.HTTP_404_NOT_FOUND)

            rule.delete()
            return Response({'message': 'Rule deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EvaluateOutcomeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff]

    def post(self, request, format=None):
        
        try:
            user=request.user
            # Check if the user is an admin of any company
            company = Company.objects.filter(admins=user).first()
            if not company:
                # Check if the user is a staff of any company
                staff_profile = CompanyStaff.objects.get(user=user)
                company = staff_profile.company
        except CompanyStaff.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            
            option_ids = request.data.get('option_ids', [])


            if not option_ids:
                return Response({"error": "No options provided."}, status=status.HTTP_400_BAD_REQUEST)


            # Retrieve all evaluation rules for the given company
            evaluation_rules = EvaluationRule.objects.filter(company=company)

            for rule in evaluation_rules:
                # Get all option IDs associated with the rule's conditions
                rule_option_ids = set(
                    EvaluationRuleCondition.objects.filter(rule=rule)
                    .values_list('option__id', flat=True)
                )

                # Check if the rule's options are a subset of the provided options
                if rule_option_ids.issubset(set(option_ids)):
                    outcome = rule.outcome
                    return Response(
                        {
                            "outcome_id": outcome.id,
                            "outcome_name": outcome.name,
                            "outcome_description": outcome.description,
                        },
                        status=status.HTTP_200_OK
                    )

            # If no rule matches, return a default response
            return Response({"message": "No matching evaluation outcome found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class ClientSubmissionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff]


    def post(self, request, format=None):
        data = request.data
        
        try:
            user = request.user
            submitted_by = user

            try:
                # Check if the user is an admin of any company
                company = Company.objects.filter(admins=user).first()
                if not company:
                    # Check if the user is a staff of any company
                    staff_profile = CompanyStaff.objects.get(user=user)
                    company = staff_profile.company
            except CompanyStaff.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
            
            evaluation_outcome = EvaluationOutcome.objects.get(id=data['generated_outcome'])
            # Create the client submission
            submission = ClientSubmission.objects.create(
                client_name=data['client_name'],
                client_email=data['email'],
                client_phone=data['phone'],
                generated_outcome=evaluation_outcome,
                updated_out_description=data['updated_out_description'],
                company=company,
                submitted_by=submitted_by,

            )

            # Add selected options to the submission
            selected_options = data['selected_options']  # List of option IDs
            for option_id in selected_options:
                option = Option.objects.get(id=option_id)
                updated_description = data.get('updated_description', {}).get(str(option_id), "")
                ClientSubmissionOption.objects.create(
                    submission=submission,
                    option=option,
                    updated_description=updated_description
                )

            return Response({"message": "Client submission created successfully", "submission_id": submission.id}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompanyListAPIView(APIView):

    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)