from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError


# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    admin = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    password = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return self.name
    
class CompanyStaff(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    password = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return super().__str__()
    
class Field(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='case_fields')
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Option(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.field} - {self.value}"


class EvaluationOutcome(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='evaluation_outcomes')
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class EvaluationRule(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='evaluation_rules')
    outcome = models.ForeignKey(EvaluationOutcome, on_delete=models.CASCADE, related_name='rules')

    def __str__(self):
        return f"Rule for {self.outcome.name}"


# Conditions for each rule
class EvaluationRuleCondition(models.Model):
    rule = models.ForeignKey(EvaluationRule, on_delete=models.CASCADE)
    option = models.ManyToManyField(Option, related_name='options')


    def __str__(self):
        options = ', '.join([option.value for option in self.option.all()])
        return f"{self.rule.outcome.name}: {options}"

