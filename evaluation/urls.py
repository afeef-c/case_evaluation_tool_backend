from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



urlpatterns = [
    path('login/',Login.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('companies/', CompanyCreateAPIView.as_view(), name='create_company'),
    path('companies/<int:company_id>/add-admin/', AddAdminAPIView.as_view(), name='add_admin'),
    path('companies/<int:company_id>/remove-admin/<int:admin_id>/', RemoveAdminAPIView.as_view(), name='remove_admin'),


    path('add_staff/', AddCompanyStaffAPIView.as_view(), name='add_company_staff'),
    path('add_fields_and_options/',AddFieldsView.as_view()),
    path('fields/', FieldListView.as_view(), name='field_list'),

    path('add_rule/',AddRulesView.as_view()),
    path('rules/',ListRulesView.as_view()),
    path('update_rule/<int:rule_id>/', UpdateRuleView.as_view(), name='update_rule'),
    path('delete_rule/<int:rule_id>/', DeleteRuleView.as_view(), name='delete_rule'),
    path('get_evaluation/', EvaluateOutcomeView.as_view(), name='get_evaluation'),

    path('submissions/', ClientSubmissionView.as_view(), name='client-submission-create'),
    
    
    path('company_details/', CompanyListAPIView.as_view(), name='comapany_details'),
    

]
