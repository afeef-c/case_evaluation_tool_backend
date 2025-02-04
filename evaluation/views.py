from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAgencyAdmin, IsCompanyAdmin
from .serializers import CompanySerializer, CompanyStaffSerializer,ClientSubmissionSerializer,ClientResponseSerializer,FieldSerializer,EvaluationRuleConditionSerialixer
from django.contrib.auth.models import User
from .models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status



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
        ''' username and password in request body
            create user with is_staff = True
            add Company instance
            request success'''
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

            company = Company.objects.create(name=data['username'], admin=admin_user, password = data['password'])

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
        #  username and password in request body
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

            company = Company.objects.get(admin_id=data.get('userId'))
            # company = Company.objects.get(admin=request.user)
            

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
            required_fields = ['userId', 'field_options', 'case_evaluation']
            if not all(field in data for field in required_fields):
                return Response({"error": "Required fields are missing."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch company and evaluate outcomes
            try:
                company = Company.objects.get(admin_id=data['userId'])
            except Company.DoesNotExist:
                return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsCompanyAdmin]


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




class ClientSubmissionAPIView(APIView):

    def post(self, request):  # Create submission with responses and options
        serializer = ClientSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            submission = serializer.save()
            return Response(ClientSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):  # Update option description
        try:
            submission = ClientSubmission.objects.get(pk=pk)
            option_id = request.data.get('option_id')
            new_description = request.data.get('custom_description')

            client_option = ClientOption.objects.get(response__submission=submission, option_id=option_id)
            client_option.custom_description = new_description
            client_option.save()

            return Response({'status': 'description updated'}, status=status.HTTP_200_OK)
        except (ClientSubmission.DoesNotExist, ClientOption.DoesNotExist):
            return Response({'error': 'Submission or Option not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):  # Final submission and storing PDF
        try:
            submission = ClientSubmission.objects.get(pk=pk)
            pdf_file = request.FILES.get('pdf_file')

            if pdf_file:
                submission.pdf_file.save(f"submission_{submission.id}.pdf", pdf_file)

            submission.is_submitted = True
            submission.save()

            return Response({'status': 'submitted', 'pdf_url': submission.pdf_file.url}, status=status.HTTP_200_OK)
        except ClientSubmission.DoesNotExist:
            return Response({'error': 'Submission not found'}, status=status.HTTP_404_NOT_FOUND)



