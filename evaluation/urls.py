from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns = [
    path('login/',Login.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('add_company/', CompanyCreateAPIView.as_view(), name='add_company'),
    path('update_company/', CompanyUpdateAPIView.as_view(), name='update_company'),
    path('delete_company/<int:company_id>/', DeleteCompanyAPIView.as_view(), name='delete_company'),

    path('add_staff/', AddCompanyStaffAPIView.as_view(), name='add_company_staff'),
    path('update_staff/', UpdateCompanyStaffAPIView.as_view(), name='update_company_staff'),
    path('delete_staff/<int:staff_id>/', DeleteStaffAPIView.as_view(), name='delete_staff'),
    path('get_company_details/', ListCompanyAPIView.as_view(), name='get_company_details'),
    
    path('upsert_fields_and_options/',AddFieldsView.as_view()),
    path('get_fields/', FieldListView.as_view(), name='field_list'),

    path('add_rule/',AddRulesView.as_view()),
    path('get_rules/',ListRulesView.as_view()),
    path('update_rule/<int:rule_id>/', UpdateRuleView.as_view(), name='update_rule'),
    
    path('delete_rule/<int:rule_id>/', DeleteRuleView.as_view(), name='delete_rule'),
    path('get_evaluation/', EvaluateOutcomeView.as_view(), name='get_evaluation'),

    path('submissions/', ClientSubmissionView.as_view(), name='client-submission-create'),
    path('get_submissions/', ClientSubmissionListView.as_view(), name='get-client-submission'),
    
    
    

]
