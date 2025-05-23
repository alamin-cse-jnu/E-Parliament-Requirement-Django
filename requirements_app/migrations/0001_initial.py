# Generated by Django 5.1.7 on 2025-04-05 08:56

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import requirements_app.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('user', 'User')], default='user', max_length=10)),
                ('designation', models.CharField(blank=True, max_length=100)),
                ('wing_name', models.CharField(blank=True, max_length=100)),
                ('department_name', models.CharField(blank=True, max_length=100)),
                ('section_name', models.CharField(blank=True, max_length=100)),
                ('mobile', models.CharField(blank=True, max_length=20)),
                ('photo', models.ImageField(blank=True, null=True, upload_to=requirements_app.models.User.get_photo_upload_path)),
                ('signature', models.ImageField(blank=True, null=True, upload_to=requirements_app.models.User.get_signature_upload_path)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='FormQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=500)),
                ('field_type', models.CharField(choices=[('text', 'Text Field'), ('textarea', 'Text Area'), ('radio', 'Radio Buttons'), ('checkbox', 'Checkboxes'), ('select', 'Dropdown'), ('number', 'Number')], max_length=20)),
                ('options', models.TextField(blank=True, help_text='For radio, checkbox, select. One option per line.')),
                ('is_required', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('help_text', models.CharField(blank=True, max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='requirements_app.formsection')),
            ],
            options={
                'ordering': ['section', 'order'],
            },
        ),
        migrations.CreateModel(
            name='RequirementForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('process_name', models.CharField(help_text='e.g., HR Management, Finance Reporting', max_length=100)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted')], default='draft', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requirement_forms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FormResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(blank=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='requirements_app.formquestion')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_responses', to='requirements_app.requirementform')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_text', models.TextField(blank=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='requirements_app.formquestion')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_responses', to='requirements_app.requirementform')),
            ],
            options={
                'unique_together': {('form', 'question')},
            },
        ),
    ]
