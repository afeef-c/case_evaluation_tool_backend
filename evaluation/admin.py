from django.contrib import admin
from .models import Company,CompanyStaff,Field,Option,EvaluationOutcome,EvaluationRule,EvaluationRuleCondition
# Register your models here.

admin.site.register(Company)
admin.site.register(CompanyStaff)
admin.site.register(Field)
admin.site.register(Option)
admin.site.register(EvaluationOutcome)
admin.site.register(EvaluationRule)
admin.site.register(EvaluationRuleCondition)