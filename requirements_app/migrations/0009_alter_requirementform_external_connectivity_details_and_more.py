# Generated by Django 5.1.7 on 2025-04-12 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requirements_app', '0008_alter_requirementform_ease_of_access_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requirementform',
            name='external_connectivity_details',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='requirementform',
            name='internal_connectivity_details',
            field=models.TextField(blank=True),
        ),
    ]
