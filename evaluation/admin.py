from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Company)
admin.site.register(CompanyStaff)
admin.site.register(Field)
admin.site.register(Option)
admin.site.register(EvaluationOutcome)
admin.site.register(EvaluationRule)
admin.site.register(EvaluationRuleCondition)
admin.site.register(ClientSubmission)

admin.site.register(ClientSubmissionOption)

