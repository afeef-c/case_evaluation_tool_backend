# Generated by Django 5.1.5 on 2025-02-03 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0003_clientoption_clientresponse_clientoption_response_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientsubmission',
            name='client_phone',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
