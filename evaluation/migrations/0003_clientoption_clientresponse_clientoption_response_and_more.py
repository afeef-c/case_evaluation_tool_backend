# Generated by Django 5.1.5 on 2025-02-03 14:31

import django.db.models.deletion
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0002_remove_evaluationrulecondition_field_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custom_description', models.TextField(blank=True, null=True)),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluation.option')),
            ],
        ),
        migrations.CreateModel(
            name='ClientResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_options', models.ManyToManyField(through='evaluation.ClientOption', to='evaluation.option')),
            ],
        ),
        migrations.AddField(
            model_name='clientoption',
            name='response',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_options', to='evaluation.clientresponse'),
        ),
        migrations.CreateModel(
            name='ClientSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=255)),
                ('client_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('client_phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='submissions/')),
                ('is_submitted', models.BooleanField(default=False)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='evaluation.company')),
            ],
        ),
        migrations.AddField(
            model_name='clientresponse',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='evaluation.clientsubmission'),
        ),
    ]
