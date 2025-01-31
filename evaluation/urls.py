from django.urls import path
from .views import *
urlpatterns = [

  
    path('company/',CompanyView.as_view()),
    path('company_staff/',CompanyStaffView.as_view()),
    path('login/',Login.as_view()),
    path('add_fields_and_options/',AddFieldsView.as_view()),
    path('add_rule/',AddRulesView.as_view())

   
    
    
]
