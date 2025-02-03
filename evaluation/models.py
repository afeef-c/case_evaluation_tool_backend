from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


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





# Client Submission Model
class ClientSubmission(models.Model):
    client_name = models.CharField(max_length=255)
    client_email = models.EmailField(null=True, blank=True)
    client_phone = PhoneNumberField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    is_submitted = models.BooleanField(default=False)  # To track if submission is final

    def __str__(self):
        return f"Submission by {self.client_name} on {self.submitted_at}"

# Client Response Model
class ClientResponse(models.Model):
    submission = models.ForeignKey(ClientSubmission, related_name='responses', on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(Option, through='ClientOption')  # Many-to-many through ClientOption


    def __str__(self):
        return f"Response for {self.submission.client_name}"

# Client Option Model
class ClientOption(models.Model):
    response = models.ForeignKey(ClientResponse, related_name='client_options', on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    custom_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.option.value} (Custom: {self.custom_description})"




