# Generated by Django 5.1.7 on 2025-04-10 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requirements_app', '0006_alter_requirementform_digital_limitation_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requirementform',
            name='current_process',
        ),
        migrations.RemoveField(
            model_name='requirementform',
            name='digital_limitation',
        ),
        migrations.RemoveField(
            model_name='requirementform',
            name='digital_software',
        ),
        migrations.RemoveField(
            model_name='requirementform',
            name='manual_limitation',
        ),
        migrations.AddField(
            model_name='requirementform',
            name='ease_of_access',
            field=models.CharField(blank=True, help_text='e.g., Difficult', max_length=100),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='error_possibility',
            field=models.CharField(blank=True, help_text='e.g., 20%', max_length=100),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='expected_analysis',
            field=models.TextField(blank=True, help_text='What kind of analysis you expect'),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='expected_features',
            field=models.TextField(blank=True, help_text='List of features you expect based on your process description'),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='expected_reports',
            field=models.TextField(blank=True, help_text='Expected reports from the new system'),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='external_connectivity',
            field=models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], default='no', max_length=10),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='external_connectivity_details',
            field=models.TextField(blank=True, help_text='Which offices need to be connected and what are the tasks'),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='internal_connectivity',
            field=models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], default='no', max_length=10),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='internal_connectivity_details',
            field=models.TextField(blank=True, help_text='Which offices need to be connected and what are the tasks'),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='people_involved',
            field=models.CharField(blank=True, help_text='e.g., 10-12 person', max_length=100),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='process_description',
            field=models.TextField(blank=True, help_text='Detailed description of the process'),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='process_steps',
            field=models.CharField(blank=True, help_text='e.g., 15-18 steps', max_length=100),
        ),
        migrations.AddField(
            model_name='requirementform',
            name='time_taken',
            field=models.CharField(blank=True, help_text='e.g., 3 days', max_length=100),
        ),
    ]
