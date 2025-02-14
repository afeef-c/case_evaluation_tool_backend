
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAgencyAdmin, IsCompanyAdmin,IsCompanyAdminOrStaff
from .serializers import *
from django.contrib.auth.models import User
from .models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
import base64
import io
from django.core.files.base import ContentFile
from rest_framework_simplejwt.views import TokenObtainPairView



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


# login view
class Login(APIView):
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                token = RefreshToken.for_user(user)

                # Add role and username inside the access token
                token['username'] = user.username
                if user.is_superuser:
                    token['role'] = "Agency Admin"
                elif user.is_staff and hasattr(user, 'company'):
                    token['role'] = "Company Admin"
                elif hasattr(user, 'staff_profile'):
                    token['role'] = "Company Staff"
                else:
                    token['role'] = None

                return Response({
                    'message': 'You are successfully logged in.',
                    'refresh': str(token),
                    'access': str(token.access_token)
                }, status=200)
            else:
                return Response({'message': 'Invalid username or password.'}, status=404)

        except Exception as e:
            return Response({
                'error': str(e) + ' missing',
                'message': "Incomplete request data"
            }, status=400)





# add company
class CompanyCreateAPIView(APIView):
    permission_classes = [IsAgencyAdmin]

    @transaction.atomic
    def post(self, request):
        serializer = CompanySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        company_data = serializer.validated_data

        try:
            # Ensure user exists or create one
            user, created = User.objects.get_or_create(username=company_data['username'])

            if created:
                user.set_password(company_data['password'])
                user.is_staff = True
                user.save()

            # Check if the user is already assigned to another company
            if Company.objects.filter(admin=user).exists():
                return Response(
                    {"error": "This admin is already assigned to another company."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create a new company
            company = Company.objects.create(
                company_name=company_data['company_name'],
                admin=user
            )

            return Response(CompanySerializer(company).data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response(
                {"error": "Database error: Possible duplicate entry."},
                status=status.HTTP_400_BAD_REQUEST
            )

# update company
class CompanyUpdateAPIView(APIView):
    permission_classes = [IsAgencyAdmin]

    @transaction.atomic
    def patch(self, request):
        try:
            company = Company.objects.get(id=request.data.get("id"))
        except Company.DoesNotExist:
            return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanySerializer(company, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        company_data = serializer.validated_data

        try:
            # Update company fields
            company.company_name = company_data.get("company_name", company.company_name)

            if "name" in company_data:
                company.name = company_data["name"]

            # Update user details
            user = company.admin
            user.username = company_data.get("username", user.username)

            if "password" in company_data:
                user.set_password(company_data["password"])

            user.save()
            company.save()

            return Response(CompanySerializer(company).data, status=status.HTTP_200_OK)

        except IntegrityError:
            return Response(
                {"error": "Database error: Possible duplicate entry."},
                status=status.HTTP_400_BAD_REQUEST
            )


# delete comapany
class DeleteCompanyAPIView(APIView):
    permission_classes = [IsAgencyAdmin]
    
    def delete(self, request, company_id):

        try:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

            company.delete()
            return Response({'message': 'Company deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class CompanyDataAPIView(APIView):
    permission_classes = [IsCompanyAdmin | IsAgencyAdmin]

    @transaction.atomic
    def post(self, request):
        try:
            company = Company.objects.get(admin=request.user)
        except Company.DoesNotExist:
            return Response({"error": "You are not authorized to modify this data."}, status=status.HTTP_403_FORBIDDEN)

        # Get or create the company data
        company_data, created = CompanyData.objects.get_or_create(company=company)

        serializer = CompanyDataSerializer_(company_data, data=request.data, partial=True)  # Allow partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        """
        If the user is SuperAdmin, return all CompanyData.
        If the user is an Agency Admin, return only their company's data.
        """
        if request.user.is_superuser:
            company_data = CompanyData.objects.all()  # SuperAdmin gets all data
        else:
            try:
                company = Company.objects.get(admin=request.user)
                company_data = CompanyData.objects.filter(company=company)  # Agency Admin gets only their company data
            except Company.DoesNotExist:
                return Response({"error": "You are not authorized to view this data."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CompanyDataSerializer_(company_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# add companystaff
class AddCompanyStaffAPIView(APIView):
    permission_classes = [IsCompanyAdmin]

    @transaction.atomic
    def post(self, request):
        try:
            # Get the company associated with the logged-in admin
            company = Company.objects.get(admin=request.user)
        except Company.DoesNotExist:
            return Response({"error": "You are not authorized to add staff."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CompanyStaffSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        company_staff_data = serializer.validated_data
        username = company_staff_data.get('username')
        password = company_staff_data.get('password')
        name = company_staff_data.get('name')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Ensure user exists or create a new one
            user, created = User.objects.get_or_create(username=username)

            if created:
                user.set_password(password)
                user.save()

            # Prevent assigning the same user to multiple companies
            if CompanyStaff.objects.filter(user=user).exists():
                return Response(
                    {"error": "This staff is already assigned to another company."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the staff entry
            company_staff = CompanyStaff.objects.create(
                name=name,
                user=user,
                company=company
            )

            return Response(
                {"message": "Staff added successfully!", "staff": CompanyStaffSerializer(company_staff).data},
                status=status.HTTP_201_CREATED
            )

        except IntegrityError:
            return Response(
                {"error": "Database error: Possible duplicate entry."},
                status=status.HTTP_400_BAD_REQUEST
            )


# update company staff
class UpdateCompanyStaffAPIView(APIView):
    permission_classes = [IsCompanyAdmin]

    @transaction.atomic
    def patch(self, request):
        try:
            # Get the company associated with the logged-in admin
            company = Company.objects.get(admin=request.user)
        except Company.DoesNotExist:
            return Response({"error": "You are not authorized to update staff."}, status=status.HTTP_403_FORBIDDEN)

        # Get staff_id from request data
        staff_id = request.data.get("staff_id")
        if not staff_id:
            return Response({"error": "Staff ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the staff member, ensuring they belong to the admin's company
        try:
            staff = CompanyStaff.objects.get(id=staff_id, company=company)
        except CompanyStaff.DoesNotExist:
            return Response({"error": "Staff member not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate and update using serializer
        serializer = CompanyStaffSerializer(staff, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        staff_data = serializer.validated_data

        try:
            # Update staff details
            staff.name = staff_data.get("name", staff.name)

            # Update user details
            user = staff.user
            user.username = staff_data.get("username", user.username)

            if "password" in staff_data:
                user.set_password(staff_data["password"])

            user.save()
            staff.save()

            return Response(CompanyStaffSerializer(staff).data, status=status.HTTP_200_OK)

        except IntegrityError:
            return Response(
                {"error": "Database error: Possible duplicate entry."},
                status=status.HTTP_400_BAD_REQUEST
            )


# delete staff
class DeleteStaffAPIView(APIView):
    permission_classes = [IsCompanyAdmin]
    
    def delete(self, request, staff_id):

        try:
            try:
                staff = CompanyStaff.objects.get(id=staff_id)
            except CompanyStaff.DoesNotExist:
                return Response({"error": "Staff not found."}, status=status.HTTP_404_NOT_FOUND)

            staff.delete()
            return Response({'message': 'Staff deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


# List company details admin and staffs
class ListCompanyAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff | IsAgencyAdmin]

    def get(self, request):
        user = self.request.user
        if user.is_superuser:
            companies = Company.objects.all()
            serializer = CompanyDataSerializer(companies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            # If user is a Company Admin or Staff, fetch details for their company
            if hasattr(user, "company"):
                company = user.company
            elif hasattr(user, "staff_profile"):
                company = user.staff_profile.company
            else:
                return Response({"error": "User is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)

            serializer = CompanyDataSerializer(company)  
            return Response(serializer.data, status=status.HTTP_200_OK)



# add/update feilds options and evaluation outcomes
class AddFieldsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]

    def post(self, request):
        try:
            data = request.data
            company = Company.objects.get(admin=request.user)


            # Add new fields and options
            for field_data in data.get('field_options', []):
                field_id = field_data.get('id')
                name=field_data['name']
                if name!="Case Evaluation":
                    if field_id:
                        field = Field.objects.filter(id=field_id, company=company).first()
                        if field:
                            field.name = name
                            field.save()
                        else:
                            return Response({"error": f"Field with id {field_id} not found."}, status=404)
                    else:
                        field = Field.objects.create(company=company, name=name)
                    
                    for option_data in field_data.get('options', []):
                        option_id = option_data.get('id')
                        if option_id:
                            option = Option.objects.filter(id=option_id, field=field).first()
                            if option:
                                option.value = option_data['name']
                                option.description = option_data['description']
                                option.save()
                            else:
                                return Response({"error": f"Option with id {option_id} not found."}, status=404)
                        else:
                            Option.objects.create(field=field, value=option_data['name'], description=option_data['description'])
                
                else:
                    
                    for eval_option in field_data.get('options', []):
                        eval_id = eval_option.get('id')
                        if eval_id:
                            eval_outcome = EvaluationOutcome.objects.filter(id=eval_id, company=company).first()
                            if eval_outcome:
                                eval_outcome.name = eval_option['name']
                                eval_outcome.description = eval_option['description']
                                eval_outcome.save()
                            else:
                                return Response({"error": f"EvaluationOutcome with id {eval_id} not found."}, status=404)
                        EvaluationOutcome.objects.create(company=company, name=eval_option['name'], description=eval_option['description'])


            return Response({"message": "Fields and options added successfully."}, status=201)

        except Company.DoesNotExist:
            return Response({"error": "Company not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# Get all feilds,options and evalaution outcomes
class FieldListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff | IsAgencyAdmin]

    def get(self, request):
        user = self.request.user
        
        if user.is_superuser:
            fields = Field.objects.all()
            evaluations = EvaluationOutcome.objects.all()
        else:
            if hasattr(user, "company"):
                company = user.company
            elif hasattr(user, "staff_profile"):
                company = user.staff_profile.company
            else:
                return Response({"error": "User is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)

            fields = Field.objects.filter(company=company)
            evaluations = EvaluationOutcome.objects.filter(company=company)
        
        # Serialize Fields
        fields_serializer = FieldSerializer(fields, many=True)
        
        # Transform Evaluations into Field-like structure
        transformed_evaluations = [{
            "id":None,
            "name": "Case Evaluation",
            "company": evaluations[0].company.id if evaluations and evaluations[0].company else None,
            "options": [
                {
                    "id": eval_obj.id,
                    # "field": eval_obj.id,
                    "value": eval_obj.name,
                    "description": eval_obj.description
                }
                for eval_obj in evaluations
            ]
        }] if evaluations else None  # Ensure it doesn't break if evaluations is empty

            
        
        
        # Merge Fields and Transformed Evaluations
        combined_data = fields_serializer.data + transformed_evaluations

        return Response(combined_data, status=status.HTTP_200_OK)





class ListEvluationRulesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff | IsAgencyAdmin]


    def get(self, request):
        user = self.request.user
        if user.is_superuser:
            rules = EvaluationOutcome.objects.all()
        else:
            # If user is a Company Admin or Staff, fetch feilds only for their company
            if hasattr(user, "company"):
                company = user.company
            elif hasattr(user, "staff_profile"):
                company = user.staff_profile.company
            else:
                return Response({"error": "User is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)

            rules= EvaluationOutcome.objects.filter(company=company)


        serializer = EvaluationOutcomeSerializer(rules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddRulesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]

    
    def post(self, request):
        try:
            data = request.data

            # Ensure required fields exist
            required_fields = [ 'field_options']
            if not all(field in data for field in required_fields):
                return Response({"error": "Required fields are missing."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            
            try:
                # Check if the user is an admin of any company
                company = Company.objects.filter(admin=user).first()
                
            except CompanyStaff.DoesNotExist:
                return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

            # Collect options
            options = []
            for field_option in data.get('field_options', []):
                if field_option.get('name')!="Case Evaluation":
                    option_name = field_option.get("option")
                    option_id = field_option.get("option_id")

                    try:
                        option = Option.objects.get(id= option_id ,value=option_name)
                        options.append(option)
                    except Option.DoesNotExist:
                        return Response({"error": f"Option '{option_id}' not found."}, status=status.HTTP_404_NOT_FOUND)

                
                else:
                    eval_id = field_option.get("option_id")
                    option_name = field_option.get("option")
                
                    evaluation_outcome = EvaluationOutcome.objects.filter(company=company,id=eval_id).first()

            if evaluation_outcome:
                # Create rule
                rule = EvaluationRule.objects.create(company=company, outcome=evaluation_outcome)
            else:
                return Response({"error": f"EvaluationOutcome with id {eval_id} not found."}, status=404)

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff | IsAgencyAdmin]


    def get(self, request):
        user = self.request.user

        if user.is_superuser:  
            rules = EvaluationRuleCondition.objects.all()
        else:  
            # If user is a Company Admin or Staff, fetch rules only for their company
            if hasattr(user, "company"):
                company = user.company
            elif hasattr(user, "staff_profile"):
                company = user.staff_profile.company
            else:
                return Response({"error": "User is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)

            # rules = EvaluationRuleCondition.objects.filter(company=company)
            rules = EvaluationRuleCondition.objects.filter(rule__company=company)


        serializer = EvaluationRuleConditionSerializer(rules, many=True)
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
            company = Company.objects.filter(admin=user).first()
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

            # Identify the company (either as an admin or staff)
            company = Company.objects.filter(admin=user).first()
            if not company:
                try:
                    staff_profile = CompanyStaff.objects.get(user=user)
                    company = staff_profile.company
                except CompanyStaff.DoesNotExist:
                    return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

            # Create the client submission
            with transaction.atomic():
                submission = ClientSubmission.objects.create(
                    client_name=data['client_name'],
                    client_email=data['email'],
                    client_phone=data['phone'],
                    company=company,
                    submitted_by=submitted_by,
                )

                # Add selected options to the submission
                field_options = data.get('field_options', [])  # List of option dictionaries

                for field_option in field_options:
                    try:
                        field_id = field_option.get('field_id')
                        name = field_option.get('name')
                        option_val = field_option.get('option')
                        n_description = field_option.get('description', "")

                        if not field_id or not name or not option_val:
                            return Response({'error': 'Missing required field in field_options'},
                                            status=status.HTTP_400_BAD_REQUEST)

                        if name != "Case Evaluation":
                            # Fetch the field option
                            option = Option.objects.get(field_id=field_id, value=option_val)

                            # Check if description was updated
                            updated_description = n_description if option.description != n_description else ""

                            # Create ClientSubmissionOption
                            ClientSubmissionOption.objects.create(
                                submission=submission,
                                option=option,
                                updated_description=updated_description
                            )

                        else:
                            # Case Evaluation logic
                            evaluation = EvaluationOutcome.objects.filter(id=field_id, name=option_val).first()
                            if not evaluation:
                                return Response({'error': f'Evaluation outcome not found for field_id {field_id}'},
                                                status=status.HTTP_400_BAD_REQUEST)

                            updated_out_description = n_description if evaluation.description != n_description else ""

                            submission.updated_out_description = updated_out_description
                            submission.generated_outcome = evaluation
                            submission.save()

                    except Option.DoesNotExist:
                        return Response({'error': f'Option "{option_val}" not found for field_id {field_id}'},
                                        status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Client submission created successfully", "submission_id": submission.id},
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class ClientSubmissionListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff]

    def get(self, request):
        try:
            user = request.user


            if user.is_superuser:  
                # Fetch submissions for the identified company
                submissions = ClientSubmission.objects.all()

            else:  
                # If user is a Company Admin or Staff, fetch rules only for their company
                if hasattr(user, "company"):
                    company = user.company
                    submissions = ClientSubmission.objects.filter(company=company)
                elif hasattr(user, "staff_profile"):
                    company = user.staff_profile.company
                    submissions = ClientSubmission.objects.filter(submitted_by=user)

                else:
                    return Response({"error": "User is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)




                serializer = ClientSubmissionSerializer(submissions, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClientSubmissionListByIdView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff]

    def get(self, request, submission_id):
        try:
            user = request.user

            if user.is_superuser:  
                submission = ClientSubmission.objects.get(id=submission_id)

            else:  
                if hasattr(user, "company"):  # If the user is a Company Admin
                    company = user.company
                    submission = ClientSubmission.objects.get(company=company, id=submission_id)
                elif hasattr(user, "staff_profile"):  # If the user is Company Staff
                    company = user.staff_profile.company
                    submission = ClientSubmission.objects.get(submitted_by=user, id=submission_id)
                else:
                    return Response({"error": "User is not associated with any company."}, status=status.HTTP_403_FORBIDDEN)

            # Serialize and return data
            serializer = ClientSubmissionSerializer(submission)  # ✅ Fixed (removed many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ClientSubmission.DoesNotExist:
            return Response({"error": "Submission not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class DeleteSubmissionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdminOrStaff | IsAgencyAdmin]

    def delete(self, request, submission_id):
        try:
            try:
                submissoin = ClientSubmission.objects.get(id=submission_id)
            except EvaluationRule.DoesNotExist:
                return Response({"error": "Submission not found."}, status=status.HTTP_404_NOT_FOUND)

            submissoin.delete()
            return Response({'message': 'Submission deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class UploadPDFView(APIView):
    def post(self, request, submission_id, format=None):
        try:
            # Get the submission instance
            submission = get_object_or_404(ClientSubmission, id=submission_id)

            # Get the base64 encoded PDF string
            base64_pdf = request.data.get('pdf_base64', None)
            if not base64_pdf:
                return Response({'error': 'No PDF data provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Decode the base64 string
            try:
                pdf_data = base64.b64decode(base64_pdf)
            except Exception as e:
                return Response({'error': f'Invalid base64 encoding: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            # Save the decoded PDF file
            pdf_file = ContentFile(pdf_data, name=f"submission_{submission_id}.pdf")
            submission.pdf_file.save(pdf_file.name, pdf_file, save=True)

            return Response({"message": "PDF uploaded successfully", "pdf_url": submission.pdf_file.url}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




