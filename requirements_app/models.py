from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    designation = models.CharField(max_length=100, blank=True)
    wing_name = models.CharField(max_length=100, blank=True)
    department_name = models.CharField(max_length=100, blank=True)
    section_name = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"
    
    @property
    def profile_image(self):
        """Returns the user's profile photo for consistent template access."""
        return self.photo

    # Add method to get custom filename for uploads
    def get_photo_upload_path(instance, filename):
        """Generate a custom path for user photos with ID in filename."""
        # Get file extension
        ext = filename.split('.')[-1]
        # Return path with user ID in filename
        return f'photos/user_{instance.id}.{ext}'
    
    def get_signature_upload_path(instance, filename):
        """Generate a custom path for user signatures with ID in filename."""
        # Get file extension
        ext = filename.split('.')[-1]
        # Return path with user ID in filename
        return f'signatures/user_{instance.id}.{ext}'
    
    # Update the fields to use the custom path functions
    photo = models.ImageField(upload_to=get_photo_upload_path, blank=True, null=True)
    signature = models.ImageField(upload_to=get_signature_upload_path, blank=True, null=True)

class FormSection(models.Model):
    """Model for dynamic form sections"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class FormQuestion(models.Model):
    """Model for dynamic questions within sections"""
    FIELD_TYPES = (
        ('text', 'Text Field'),
        ('textarea', 'Text Area'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkboxes'),
        ('select', 'Dropdown'),
        ('number', 'Number'),
    )
    
    section = models.ForeignKey(FormSection, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    options = models.TextField(blank=True, help_text="For radio, checkbox, select. One option per line.")
    is_required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    help_text = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['section', 'order']
    
    def __str__(self):
        return f"{self.section.title} - {self.question_text}"
    

class QuestionResponse(models.Model):
    """Model to store responses to dynamic questions"""
    form = models.ForeignKey('RequirementForm', on_delete=models.CASCADE, related_name='question_responses')
    question = models.ForeignKey(FormQuestion, on_delete=models.CASCADE)
    response_text = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['form', 'question']
    
    def __str__(self):
        return f"{self.form.user.username} - {self.question.question_text}"
    


class RequirementForm(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    )
    
    PROCESS_CHOICES = (
        ('manual', 'Fully Manual'),
        ('partial', 'Partially Digital'),
        ('digital', 'Fully Digital'),
    )
    
    LEVEL_CHOICES = (
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    )
    
    ACCESS_CHOICES = (
        ('difficult', 'Difficult'),
        ('moderate', 'Moderate'),
        ('easy', 'Easy'),
    )
    
    RISK_CHOICES = (
        ('high', 'High Risk'),
        ('medium', 'Medium Risk'),
        ('low', 'Low Risk'),
    )
    
    SPEED_CHOICES = (
        ('slow', 'Slow'),
        ('moderate', 'Moderate'),
        ('fast', 'Fast'),
    )
    
    REPORT_CHOICES = (
        ('manual', 'Manual & Time-Consuming'),
        ('semi', 'Semi-Automated'),
        ('auto', 'Fully Automated'),
    )
    
    INTEGRATION_CHOICES = (
        ('none', 'Not Integrated'),
        ('partial', 'Partially Integrated'),
        ('full', 'Fully Integrated'),
    )
    
    # User information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requirement_forms')
    
    
    # fields for Process Information
    process_name = models.CharField(max_length=100, blank=False)
    process_description = models.TextField(blank=False)
    process_steps_detail = models.JSONField(default=list, blank=True)
    flowchart = models.FileField(upload_to='attachments/', blank=False, null=False)
    
    # fields for Process Efficiency Analysis
    time_taken = models.PositiveIntegerField(blank=False)
    people_involved = models.PositiveIntegerField(blank=False)
    process_steps = models.PositiveIntegerField(blank=False)
    # error_possibility = models.PositiveIntegerField(blank=False)
    # ease_of_access = models.PositiveIntegerField(blank=False)
    
    # fields for Expectations from New Software
    expected_features = models.TextField(blank=False)
    internal_connectivity = models.CharField(max_length=10, choices=(('yes', 'Yes'), ('no', 'No')), default='no')
    internal_connectivity_details = models.TextField(blank=True)
    external_connectivity = models.CharField(max_length=10, choices=(('yes', 'Yes'), ('no', 'No')), default='no')
    external_connectivity_details = models.TextField(blank=True)
    
    # fields for Report and Data Analysis
    expected_reports = models.TextField(blank=False)
    expected_analysis = models.TextField(blank=False)

    # fields for Attachment
    attachment = models.FileField(upload_to='attachments/', blank=True, null=True)

    #current_process = models.CharField(max_length=20, choices=PROCESS_CHOICES, default='manual')  
    #digital_software = models.CharField(max_length=100, blank=True)
    #digital_limitation = models.TextField(blank=True)
    #manual_limitation =  models.TextField( blank=True) 

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    def submit(self):
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.status} - {self.created_at.strftime('%Y-%m-%d')}"
    
    # Custom method to generate flowchart filename
    def get_flowchart_upload_path(instance, filename):
        # Generate filename based on user ID
        return f'attachments/{instance.user.username}_DataFlow.pdf'
    
    # Update flowchart field to use custom path
    flowchart = models.FileField(upload_to=get_flowchart_upload_path, blank=False, null=True)

class FormResponse(models.Model):
    form = models.ForeignKey(RequirementForm, on_delete=models.CASCADE, related_name='form_responses')
    question = models.ForeignKey(FormQuestion, on_delete=models.CASCADE)
    answer = models.TextField(blank=True)

    def __str__(self):
        return f"{self.form} - {self.question.question_text}: {self.answer}"
    