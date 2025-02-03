# Generated by Django 5.1.5 on 2025-02-01 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evaluationrulecondition',
            name='field',
        ),
        migrations.RemoveField(
            model_name='evaluationrulecondition',
            name='option',
        ),
        migrations.AddField(
            model_name='evaluationrulecondition',
            name='option',
            field=models.ManyToManyField(related_name='options', to='evaluation.option'),
        ),
    ]
