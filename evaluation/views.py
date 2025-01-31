from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAgencyAdmin, IsCompanyAdmin
from .serializers import CompanySerializer, CompanyStaffSerializer
from django.contrib.auth.models import User
from .models import *
from rest_framework_simplejwt.authentication import JWTAuthentication

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
        

class CompanyView(APIView):
    permission_classes = [IsAgencyAdmin]
    
    #  add company with username and password
    def post(self, request):
        # username and password in request body
        # create user with is_staff = True
        # add Company instance
        # request success
        try:
            serializer = CompanySerializer(data = request.data)
            if not serializer.is_valid():
                return Response({"message": serializer.errors}, status=400)
            data = serializer.validated_data
            
            admin_user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                is_staff=True
            )

            company = Company.objects.create(name=data['username'], admin=admin_user,password = data['password'])

            return Response(
                {"message": f"Company created with admin '{company.admin.username}'"},
                status=201,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )
      
class CompanyStaffView(APIView):
    permission_classes = [IsCompanyAdmin]
    authentication_classes = [JWTAuthentication]
    
    # add staff
    def post(self, request):
        # username and password in request body
        # create user 
        # add Company staff instance associate with request users instance as company
        # request success
        try:
            serializer = CompanyStaffSerializer(request.data)
            if not serializer.is_valid():
                return Response({"message": serializer.errors}, status=400)
            data = serializer.validated_data
            
            staff_user = User.objects.create_user(
                username=data['username'],
                password=data['password']
            )
           
            company = request.user.company

            company_staff = CompanyStaff.objects.create(name=data['name'], company=company,user = staff_user, password = data['password'])

            return Response(
                {"message": f"Staff '{company_staff.name}' created with admin '{company.name}'"},
                status=201,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )
            
class AddFieldsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]
    def post(self, request):
        try:
            data = request.data
            # company = Company.objects.get(admin_id=data['userId'])
            company = Company.objects.get(admin=request.user)
            

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
    
class AddRulesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]
    def post(self, request):
        try:
            data = request.data
            
            company = Company.objects.get(admin=request.user)
            # company = Company.objects.get(admin_id=data['userId'])

            evaluation_outcome = EvaluationOutcome.objects.get(company=company, name=data['case_evaluation'])
            rule = EvaluationRule.objects.create(company=company, outcome=evaluation_outcome)

            for field_data in data.get('field_options', []):
                field = Field.objects.get(company=company, name=field_data['name'])
                rule_field = EvaluationRuleCondition.objects.create(rule=rule, field=field)
                for option_name in field_data.get('options', []):
                    option = Option.objects.get(field=field, value=option_name)
                    rule_field.option.add(option)

            return Response({"message": "Rules added successfully."}, status=201)
        except Exception as e:
                    return Response(
                        {"error": str(e)},
                        status=500
                    )
