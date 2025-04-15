from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, RequirementForm, FormSection, FormQuestion, QuestionResponse

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'first_name', 'last_name', 'email', 'role', 'designation', 'wing_name', 'department_name','section_name', 'mobile', 'photo', 'signature']
        widgets = {
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'signature': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords don't match")
        
        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'designation', 'wing_name', 'department_name', 'section_name', 'mobile', 'photo', 'signature']
        widgets = {
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
            'signature': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class RequirementFormForm(forms.ModelForm):
    """Form for the basic fields of the RequirementForm model"""
    process_steps_detail = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False
    )
    class Meta:
        model = RequirementForm
        fields = ['process_name', 'process_description', 'process_steps_detail', 'flowchart',
                'time_taken', 'people_involved', 'process_steps',
                'expected_features', 'internal_connectivity', 'internal_connectivity_details',
                'external_connectivity', 'external_connectivity_details',
                'expected_reports', 'expected_analysis', 'attachment'
                #'error_possibility', 'ease_of_access',
                ]
        widgets = {
            'process_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., HR Management, Bill Processing of House'}),
            'process_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Provide a overview of your working process'}),
            'time_taken': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 3', 'min': '0'}),
            'people_involved': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 10', 'min': '0'}),
            'process_steps': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 15', 'min': '0'}),
            # 'error_possibility': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 20', 'min': '0', 'max': '100'}),
            # 'ease_of_access': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 80', 'min': '0', 'max': '100'}),
            'expected_features': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'internal_connectivity': forms.Select(attrs={'class': 'form-control'}),
            'internal_connectivity_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'external_connectivity': forms.Select(attrs={'class': 'form-control'}),
            'external_connectivity_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'expected_reports': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe expected reports from the new system'}),
            'expected_analysis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe what kind of analysis you expect'}),
            'flowchart': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.instance_id = kwargs.pop('instance_id', None)
        super(RequirementFormForm, self).__init__(*args, **kwargs)

    def clean_process_name(self):
        process_name = self.cleaned_data.get('process_name')
        if self.user and process_name:
            # Check if there is already a submitted form with this process name by this user
            # Exclude the current instance if we're editing a draft
            query = RequirementForm.objects.filter(
                user=self.user,
                process_name=process_name,
                status='submitted'
            )
            
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
                
            if query.exists():
                raise forms.ValidationError(f"You have already submitted a form for '{process_name}'. Please use a different process name.")
        return process_name

# Base form class for dynamic questions
class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        sections = kwargs.pop('sections', None)
        instance = kwargs.pop('instance', None)
        super(DynamicForm, self).__init__(*args, **kwargs)
        
        if not sections:
            return
            
        # Dictionary to store responses if instance is provided
        responses = {}
        if instance:
            for response in instance.question_responses.all():
                responses[response.question.id] = response.response_text
                
        # Add fields for each question in each active section
        for section in sections:
            for question in section.questions.filter(is_active=True).order_by('order'):
                field_name = f"question_{question.id}"
                field_kwargs = {
                    'label': question.question_text,
                    'required': question.is_required,
                    'help_text': question.help_text,
                }
                
                # Create appropriate field based on field_type
                if question.field_type == 'text':
                    self.fields[field_name] = forms.CharField(**field_kwargs)
                elif question.field_type == 'textarea':
                    field_kwargs['widget'] = forms.Textarea(attrs={'rows': 3})
                    self.fields[field_name] = forms.CharField(**field_kwargs)
                elif question.field_type == 'radio':
                    choices = [(opt.strip(), opt.strip()) for opt in question.options.split('\n') if opt.strip()]
                    self.fields[field_name] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, **field_kwargs)
                elif question.field_type == 'checkbox':
                    choices = [(opt.strip(), opt.strip()) for opt in question.options.split('\n') if opt.strip()]
                    self.fields[field_name] = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple, **field_kwargs)
                elif question.field_type == 'select':
                    choices = [(opt.strip(), opt.strip()) for opt in question.options.split('\n') if opt.strip()]
                    self.fields[field_name] = forms.ChoiceField(choices=choices, **field_kwargs)
                elif question.field_type == 'number':
                    self.fields[field_name] = forms.IntegerField(**field_kwargs)
                    
                # Set initial value if we have a response
                if question.id in responses:
                    self.fields[field_name].initial = responses[question.id]

    def get_question_fields(self):
        """Return only the fields for questions (excluding CSRF etc.)"""
        return {k: v for k, v in self.fields.items() if k.startswith('question_')}

class FormSectionForm(forms.ModelForm):
    """Form for managing form sections in admin"""
    class Meta:
        model = FormSection
        fields = ['title', 'description', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }

class FormQuestionForm(forms.ModelForm):
    """Form for managing questions in admin"""
    class Meta:
        model = FormQuestion
        fields = ['question_text', 'field_type', 'options', 'is_required', 'order', 'help_text', 'is_active']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'options': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'One option per line'}),
            'help_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Additional information about this question'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if not username or not password:
            raise forms.ValidationError("Both username and password are required.")
        return cleaned_data
