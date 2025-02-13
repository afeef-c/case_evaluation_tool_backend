# Generated by Django 5.1.5 on 2025-02-05 11:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0007_remove_company_admin_company_admins'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientoption',
            name='response',
        ),
        migrations.RemoveField(
            model_name='company',
            name='password',
        ),
        migrations.AddField(
            model_name='clientoption',
            name='submission',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='client_options', to='evaluation.clientsubmission'),
        ),
        migrations.AddField(
            model_name='clientsubmission',
            name='selected_options',
            field=models.ManyToManyField(through='evaluation.ClientOption', to='evaluation.option'),
        ),
        migrations.AddField(
            model_name='clientsubmission',
            name='submitted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submitted_submissions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='ClientResponse',
        ),
    ]
