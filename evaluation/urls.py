from django.urls import path
from .views import *
urlpatterns = [

  
    path('companies/', CompanyCreateAPIView.as_view(), name='create_company'),
    path('companies/<int:company_id>/add-admin/', AddAdminAPIView.as_view(), name='add_admin'),
    path('companies/<int:company_id>/remove-admin/<int:admin_id>/', RemoveAdminAPIView.as_view(), name='remove_admin'),


    path('add_staff/', AddCompanyStaffAPIView.as_view(), name='add_company_staff'),
    path('login/',Login.as_view()),
    path('add_fields_and_options/',AddFieldsView.as_view()),
    path('fields/', FieldListView.as_view(), name='field_list'),

    path('add_rule/',AddRulesView.as_view()),
    path('rules/',ListRulesView.as_view()),
    path('update_rule/<int:rule_id>/', UpdateRuleView.as_view(), name='update_rule'),
    path('delete_rule/<int:rule_id>/', DeleteRuleView.as_view(), name='delete_rule'),

    path('client_submissions/', ClientSubmissionAPIView.as_view(), name='client_submission_create'),
    path('client_submissions/<int:pk>/', ClientSubmissionAPIView.as_view(), name='client_submission_detail'),
    
   
    
    
]
