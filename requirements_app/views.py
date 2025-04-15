from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import User, RequirementForm, FormSection, FormQuestion, QuestionResponse
from .forms import RequirementFormForm, UserRegistrationForm, UserUpdateForm, DynamicForm, FormQuestionForm, FormSectionForm
from .utils import generate_pdf, generate_user_list_pdf, get_static_file_as_data_uri
import json
from django.db.models import Count, Avg, Q
from collections import defaultdict
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from .forms import LoginForm  
import os
import base64
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
import tempfile
import pickle
from django.db.models.fields.files import FieldFile
from django.template.loader import render_to_string
from datetime import datetime
from weasyprint import HTML, CSS


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    # Get count of forms
    user_forms_count = RequirementForm.objects.filter(user=request.user).count()
    submitted_forms_count = RequirementForm.objects.filter(user=request.user, status='submitted').count()
    
    # Get draft forms for the user
    draft_forms = RequirementForm.objects.filter(user=request.user, status='draft').order_by('-updated_at')
    
    context = {
        'user_forms_count': user_forms_count,
        'submitted_forms_count': submitted_forms_count,
        'draft_forms': draft_forms,
    }
    return render(request, 'requirements_app/dashboard.html', context)

@login_required
def form_view(request, form_id=None):
    # If form_id is provided, get the specific form to edit (draft)
    if form_id:
        instance = get_object_or_404(RequirementForm, id=form_id, user=request.user, status='draft')
    else:
        instance = None
        
    # Check if process_name already exists when submitting
    process_name_error = None
    if request.method == 'POST' and ('submit' in request.POST or 'review' in request.POST):
        process_name = request.POST.get('process_name')
        query = RequirementForm.objects.filter(user=request.user, process_name=process_name, status='submitted')
        
        # If we're editing an existing form, exclude it from the check
        if instance:
            query = query.exclude(pk=instance.pk)
            
        if query.exists():
            process_name_error = f"You have already submitted a form for '{process_name}'. Please use a different process name."
    
    # Get all active form sections with their questions
    active_sections = FormSection.objects.filter(is_active=True).prefetch_related('questions').order_by('order')

    if request.method == 'POST':
        # If there's a process name error, don't proceed with form submission
        if process_name_error:
            messages.error(request, process_name_error)
            basic_form = RequirementFormForm(request.POST, request.FILES, instance=instance)
            dynamic_form = DynamicForm(request.POST, sections=active_sections, instance=instance)
        else:
            # Process the basic form data
            basic_form = RequirementFormForm(request.POST, request.FILES, instance=instance)
            # Process the dynamic questions
            dynamic_form = DynamicForm(request.POST, sections=active_sections, instance=instance)

            if basic_form.is_valid() and dynamic_form.is_valid():
                # Save the basic form but don't commit to DB yet
                requirement_form = basic_form.save(commit=False)
                requirement_form.user = request.user

                # Process steps detail (from dynamic JS form input)
                process_steps_detail = request.POST.get('process_steps_detail', '[]')
                try:
                    # Parse the JSON string into a Python object (list of dictionaries)
                    steps_data = json.loads(process_steps_detail)
                    
                    # Make sure steps_data is a list of dictionaries with number and description
                    valid_steps = []
                    for i, step in enumerate(steps_data):
                        if isinstance(step, dict) and 'description' in step and step['description'].strip():
                            # Ensure the step has a valid number
                            step['number'] = step.get('number', i + 1)
                            valid_steps.append(step)
                        elif isinstance(step, str) and step.strip():
                            # If it's just a string, convert to proper format
                            valid_steps.append({
                                'number': i + 1,
                                'description': step.strip()
                            })
                    
                    # Store the validated steps
                    requirement_form.process_steps_detail = valid_steps
                    # Sync step count with detailed steps
                    requirement_form.process_steps = len(valid_steps)
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, initialize with empty list
                    requirement_form.process_steps_detail = []
                    requirement_form.process_steps = 0
                
                # Handle Save as Draft
                if 'save_draft' in request.POST:
                    requirement_form.status = 'draft'  
                    
                    # Handle file uploads
                    if 'attachment' in request.FILES:
                        file = request.FILES['attachment']
                        if file.name.endswith('.pdf'):
                            filename = f"{request.user.username}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
                            content = file.read()
                            requirement_form.attachment.save(filename, ContentFile(content), save=False)
                        else:
                            messages.error(request, "Attachment must be a PDF file.")
                            return redirect('form_view' if not form_id else 'form_view', form_id=form_id)
                        
                    # Handle flowchart upload (optional)
                    if 'flowchart' in request.FILES:
                        file = request.FILES['flowchart']
                        if not file.name.endswith('.pdf'):
                            messages.error(request, "Flowchart must be a PDF file.")
                            return redirect('form_view' if not form_id else 'form_view', form_id=form_id)
                    
                    requirement_form.save()

                    # Save responses for dynamic questions
                    for field_name, value in dynamic_form.cleaned_data.items():
                        if field_name.startswith('question_'):
                            question_id = int(field_name.split('_')[1])
                            question = FormQuestion.objects.get(id=question_id)

                            # Convert list values to string for checkboxes
                            if isinstance(value, list):
                                value = ', '.join(value)

                            # Create or update response
                            QuestionResponse.objects.update_or_create(
                                form=requirement_form,
                                question=question,
                                defaults={'response_text': value if value is not None else ''}
                            )

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'message': 'Form saved as draft successfully.'})
                    messages.success(request, "Form saved as draft successfully.")
                    return redirect('dashboard')
                
                # Handle review option - store data in session and redirect to review page
                elif 'review' in request.POST:
                    # Store form data in session
                    form_data = {}

                    # Copy basic form data from POST (avoiding file fields completely)
                    for key in request.POST:
                        if key not in ['csrfmiddlewaretoken', 'save_draft', 'review', 'submit']:
                            form_data[key] = request.POST[key]
                    
                    # Store the processed steps data correctly
                    try:
                        steps_data = json.loads(process_steps_detail)
                        form_data['process_steps_detail'] = steps_data
                    except json.JSONDecodeError:
                        form_data['process_steps_detail'] = []
                    
                    # Handle file flags
                    form_data['has_flowchart'] = bool(request.FILES.get('flowchart')) or (instance and bool(instance.flowchart))
                    form_data['has_attachment'] = bool(request.FILES.get('attachment')) or (instance and bool(instance.attachment))
                
                    # Store form_id if we're editing an existing draft
                    if instance:
                        form_data['form_id'] = instance.id
                        
                        # Set file flags based on existing files
                        if not form_data['has_flowchart'] and instance.flowchart:
                            form_data['has_flowchart'] = True
                        if not form_data['has_attachment'] and instance.attachment:
                            form_data['has_attachment'] = True
                    
                    # Store dynamic form responses
                    question_responses = {}
                    for key, value in request.POST.items():
                        if key.startswith('question_'):
                            question_id = key.split('_')[1]
                            question_responses[question_id] = value
                            
                            # Convert list values to string for checkboxes
                            if isinstance(value, list):
                                value = ', '.join(value)
                                
                            question_responses[question_id] = value if value is not None else ''
                    
                    # Store files temporarily
                    temp_files = {}
                    if 'flowchart' in request.FILES:
                        temp_file = tempfile.NamedTemporaryFile(delete=False)
                        for chunk in request.FILES['flowchart'].chunks():
                            temp_file.write(chunk)
                        temp_file.close()
                        temp_files['flowchart'] = temp_file.name
                    
                    if 'attachment' in request.FILES:
                        temp_file = tempfile.NamedTemporaryFile(delete=False)
                        for chunk in request.FILES['attachment'].chunks():
                            temp_file.write(chunk)
                        temp_file.close()
                        temp_files['attachment'] = temp_file.name
                    
                    # Store everything in session
                    request.session['form_data'] = form_data
                    request.session['question_responses'] = question_responses
                    request.session['temp_files'] = temp_files
                    request.session['review_timestamp'] = timezone.now().isoformat()
                    
                    # Redirect to review page
                    return redirect('review_form')
            else:
                # If forms are invalid, display errors
                for field, errors in basic_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

                for field, errors in dynamic_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

    else:
        # Initial form load 
        basic_form = RequirementFormForm(instance=instance)
        dynamic_form = DynamicForm(sections=active_sections, instance=instance)
        
    # Group questions by section
    sections_with_questions = []
    for section in active_sections:
        questions = []
        for question in section.questions.filter(is_active=True).order_by('order'):
            field_name = f"question_{question.id}"
            if field_name in dynamic_form.fields:
                questions.append({
                    'question': question,
                    'field': dynamic_form[field_name]
                })

        if questions:  # Only add sections with active questions
            sections_with_questions.append({
                'section': section,
                'questions': questions
            })

    context = {
        'basic_form': basic_form,
        'dynamic_form': dynamic_form,
        'sections_with_questions': sections_with_questions,
        'is_draft': instance is not None,  # True if editing a draft
        'form_id': form_id,  # Pass form_id to template
        'process_name_error': process_name_error,
    }

    return render(request, 'requirements_app/form.html', context)

@login_required
def view_submissions(request):
    forms = RequirementForm.objects.filter(user=request.user, status='submitted').order_by('-submitted_at')
    
    # Add attachment flags for each form
    for form in forms:
        form.has_attachment = bool(form.attachment)
        form.has_flowchart = bool(form.flowchart)
    
    context = {
        'forms': forms,
    }
    return render(request, 'requirements_app/view_submissions.html', context)

# Update view_responses for admin to see process name and user ID
@user_passes_test(is_admin)
def view_responses(request):
    forms = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    # Filter by process name if provided
    process_filter = request.GET.get('process')
    if process_filter:
        forms = forms.filter(process_name__icontains=process_filter)
    
    # Filter by user ID if provided
    user_filter = request.GET.get('user_id')
    if user_filter:
        forms = forms.filter(user__username__icontains=user_filter)
    
    # Check attachment existence for each form
    for form in forms:
        form.has_attachment = bool(form.attachment)
        form.has_flowchart = bool(form.flowchart)
    
    # Get unique process names for filtering
    all_process_names = RequirementForm.objects.filter(status='submitted').values_list('process_name', flat=True).distinct()
    
    context = {
        'forms': forms,
        'all_process_names': all_process_names,
        'process_filter': process_filter,
        'user_filter': user_filter,
    }
    return render(request, 'requirements_app/view_responses.html', context)

@login_required
def view_form(request, form_id=None):
    if form_id:
        form = get_object_or_404(RequirementForm, id=form_id, user=request.user)
    else:
        # If no ID provided, redirect to submissions page
        return redirect('view_submissions')
    
    # Get all sections with questions
    sections = FormSection.objects.filter(is_active=True).order_by('order')
    
    # Create a data structure to hold sections with their answers
    sections_with_answers = []
    
    for section in sections:
        section_answers = []
        for question in section.questions.filter(is_active=True):
            try:
                answer = QuestionResponse.objects.get(form=form, question=question)
                section_answers.append({
                    'question': question,
                    'answer_text': answer.response_text
                })
            except QuestionResponse.DoesNotExist:
                # Skip questions with no answers
                continue
                
        # Only add sections that have at least one answer
        if section_answers:
            sections_with_answers.append({
                'section': section,
                'answers': section_answers
            })
    
    context = {
        'form': form,
        'sections_with_answers': sections_with_answers,
        # data is available for template
        'user': request.user
    }
    return render(request, 'requirements_app/view_form.html', context)

@user_passes_test(is_admin)
def view_user_form(request, form_id):
    form = get_object_or_404(RequirementForm, pk=form_id)
    
    # Get all sections with questions
    sections = FormSection.objects.filter(is_active=True).order_by('order')
    
    # Create a data structure to hold sections with their answers
    sections_with_answers = []
    
    for section in sections:
        section_answers = []
        for question in section.questions.filter(is_active=True):
            try:
                answer = QuestionResponse.objects.get(form=form, question=question)
                section_answers.append({
                    'question': question,
                    'answer_text': answer.response_text
                })
            except QuestionResponse.DoesNotExist:
                # Skip questions with no answers
                continue
                
        # Only add sections that have at least one answer
        if section_answers:
            sections_with_answers.append({
                'section': section,
                'answers': section_answers
            })
    
    context = {
        'form': form,
        'sections_with_answers': sections_with_answers
    }
    return render(request, 'requirements_app/view_user_form.html', context)

@login_required
def download_pdf(request, form_id):
    form = get_object_or_404(RequirementForm, id=form_id, user=request.user)
    
    # Get all sections with questions and answers (same as view_form)
    sections = FormSection.objects.filter(is_active=True).order_by('order')
    sections_with_answers = []
    for section in sections:
        section_answers = []
        for question in section.questions.filter(is_active=True):
            try:
                answer = QuestionResponse.objects.get(form=form, question=question)
                section_answers.append({
                    'question': question,
                    'answer_text': answer.response_text
                })
            except QuestionResponse.DoesNotExist:
                continue
        if section_answers:
            sections_with_answers.append({
                'section': section,
                'answers': section_answers
            })

    # Generate the signature data URI
    signature_data_uri = None
    if request.user.signature:  # Check if the user has a signature
        signature_path = os.path.join(settings.MEDIA_ROOT, request.user.signature.name)
        if os.path.exists(signature_path):
            with open(signature_path, 'rb') as image_file:
                signature_data = base64.b64encode(image_file.read()).decode('utf-8')
                signature_data_uri = f"data:image/png;base64,{signature_data}"  # Adjust MIME type if needed
        else:
            print(f"Signature file not found at: {signature_path}")

    # Prepare context for the template
    context = {
        'form': form,
        'sections_with_answers': sections_with_answers,
        'user': request.user,  # Match view_form.html
        'current_date': timezone.now(),
        'signature_data_uri': signature_data_uri,
    }
    # Generate PDF using the utility function
    pdf = generate_pdf(form)
    
    # Create HTTP response with PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="requirement_form_{request.user.username}_{form.process_name}.pdf"'
    
    return response

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = User.objects.filter(role='user').count()
    total_admins = User.objects.filter(role='admin').count()
    submitted_forms = RequirementForm.objects.filter(status='submitted').count()
    draft_forms = RequirementForm.objects.filter(status='draft').count()
    response_rate = (submitted_forms / total_users) * 100 if total_users > 0 else 0
    
    # Forms by wing and department
    forms_by_wing = RequirementForm.objects.filter(status='submitted').values('user__wing_name').annotate(count=Count('id'))
    forms_by_department = RequirementForm.objects.filter(status='submitted').values('user__department_name').annotate(count=Count('id'))
    
    # Process name statistics
    process_names = RequirementForm.objects.filter(status='submitted').values('process_name').annotate(count=Count('id'))
    
    # Prepare data for charts as JSON
    wing_labels = [item['user__wing_name'] or 'Unknown' for item in forms_by_wing]
    wing_data = [item['count'] for item in forms_by_wing]
    
    dept_labels = [item['user__department_name'] or 'Unknown' for item in forms_by_department]
    dept_data = [item['count'] for item in forms_by_department]
    
    process_labels = [item['process_name'] or 'Unnamed Process' for item in process_names]
    process_data = [item['count'] for item in process_names]
    
    # Count total sections and questions in the system
    total_sections = FormSection.objects.count()
    total_questions = FormQuestion.objects.count()
    active_sections = FormSection.objects.filter(is_active=True).count()
    active_questions = FormQuestion.objects.filter(is_active=True).count()
    
    context = {
        'total_users': total_users,
        'total_admins': total_admins,
        'submitted_forms': submitted_forms,
        'draft_forms': draft_forms,
        'response_rate': response_rate,
        'total_sections': total_sections,
        'total_questions': total_questions,
        'active_sections': active_sections,
        'active_questions': active_questions,
        'chart_data': {
            'wing_labels': wing_labels,
            'wing_data': wing_data,
            'dept_labels': dept_labels,
            'dept_data': dept_data,
            'process_labels': process_labels,
            'process_data': process_data,
        },
    }
    return render(request, 'requirements_app/admin_dashboard.html', context)


@user_passes_test(is_admin)
def user_management(request):
    users = User.objects.all().order_by('role', 'username')
    
    context = {
        'users': users,
    }
    return render(request, 'requirements_app/user_management.html', context)


@user_passes_test(is_admin)
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user but don't save to DB yet
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            
            # First save to generate ID
            user.save()
            
            # Process the uploaded files if they exist
            if 'photo' in request.FILES:
                # Save again to ensure the custom path with ID is used
                user.photo = request.FILES['photo']
                
            if 'signature' in request.FILES:
                user.signature = request.FILES['signature']
                
            # Save the final user object with all updates
            user.save()
            
            messages.success(request, f"User '{user.username}' created successfully.")
            return redirect('user_management')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'requirements_app/register_user.html', context)


@user_passes_test(is_admin)
def reset_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        user.set_password(new_password)
        user.save()
        messages.success(request, f"Password for '{user.username}' reset successfully.")
        return redirect('user_management')
    
    context = {
        'user': user,
    }
    return render(request, 'requirements_app/reset_password.html', context)

@user_passes_test(is_admin)
def change_role(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        user.role = 'admin' if user.role == 'user' else 'user'
        user.save()
        messages.success(request, f"Role updated for '{user.username}' to {user.role}.")
    
    return redirect('user_management')

@user_passes_test(is_admin)
def view_responses(request):
    forms = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    # Filter by process name if provided
    process_filter = request.GET.get('process')
    if process_filter:
        forms = forms.filter(process_name__icontains=process_filter)
    
    #Check attachment existence for each form
    for form in forms:
        if form.attachment and form.attachment.name:
            form.has_attachment = True
        else:
            form.has_attachment = False
    # Get unique process names for filtering
    all_process_names = RequirementForm.objects.filter(status='submitted').values_list('process_name', flat=True).distinct()
    
    context = {
        'forms': forms,
        'all_process_names': all_process_names,
        'process_filter': process_filter,
    }
    return render(request, 'requirements_app/view_responses.html', context)


@user_passes_test(is_admin)
def delete_form(request, form_id):
    form = get_object_or_404(RequirementForm, pk=form_id)
    
    if request.method == 'POST':
        form.delete()
        messages.success(request, "Form deleted successfully.")
        return redirect('view_responses')
    
    context = {
        'form': form,
    }
    return render(request, 'requirements_app/delete_form_confirm.html', context)

@user_passes_test(is_admin)
def data_analysis(request):
    # Get some general statistics
    total_users = User.objects.filter(role='user').count()
    submitted_forms = RequirementForm.objects.filter(status='submitted').count()
    response_rate = (submitted_forms / total_users) * 100 if total_users > 0 else 0
    avg_completion_time = "5.2"  # This is a placeholder - calculate actual value if needed
    
    # Forms by wing and department
    forms_by_wing = RequirementForm.objects.filter(status='submitted').values('user__wing_name').annotate(count=Count('id'))
    forms_by_department = RequirementForm.objects.filter(status='submitted').values('user__department_name').annotate(count=Count('id'))
    
    # Process names
    process_names = RequirementForm.objects.filter(status='submitted').values('process_name').annotate(count=Count('id')).order_by('-count')[:8]
    
    # Prepare data for charts
    wing_labels = [item['user__wing_name'] or 'Unknown' for item in forms_by_wing]
    wing_data = [item['count'] for item in forms_by_wing]
    
    dept_labels = [item['user__department_name'] or 'Unknown' for item in forms_by_department]
    dept_data = [item['count'] for item in forms_by_department]
    
    process_names_data = [item['process_name'] for item in process_names]
    process_counts_data = [item['count'] for item in process_names]

    # Get all questions with responses
    questions = FormQuestion.objects.filter(
        id__in=QuestionResponse.objects.values_list('question', flat=True).distinct()
    )
    # Prepare question analysis data
    question_analysis = []
    for question in questions:
    
        # Get all responses for this question
        responses = QuestionResponse.objects.filter(question=question)
    
        # For choice-based questions (radio, select, checkbox)
        if question.field_type in ['radio', 'select', 'checkbox']:
            # Count occurrences of each option
            option_counts = {}
            for response in responses:
                # Split by comma for checkbox responses
                if question.field_type == 'checkbox' and ',' in response.response_text:
                    options = [opt.strip() for opt in response.response_text.split(',')]
                    for opt in options:
                        option_counts[opt] = option_counts.get(opt, 0) + 1
                else:
                    option_counts[response.response_text] = option_counts.get(response.response_text, 0) + 1
        
            # Calculate percentages
            total = sum(option_counts.values())
            options_data = []
            colors = ['primary', 'success', 'warning', 'danger', 'info', 'secondary']
        
            for i, (option, count) in enumerate(option_counts.items()):
                percentage = (count / total) * 100 if total > 0 else 0
                options_data.append({
                    'text': option,
                    'count': count,
                    'percentage': percentage,
                    'color': colors[i % len(colors)]
                })
        
            question_analysis.append({
                'text': question.question_text,
                'total_responses': total,
                'options': options_data
            })
    
        # For text-based questions, just count total responses
        else:
            question_analysis.append({
                'text': question.question_text,
                'total_responses': responses.count(),
                'options': []  # Empty options for text fields
            })
    
    # Prepare data for Time Efficiency Analysis chart
    time_vs_steps_data = []
    for form in RequirementForm.objects.filter(status='submitted'):
        if form.time_taken is not None and form.process_steps is not None:
            time_vs_steps_data.append({
                'x': form.process_steps,
                'y': form.time_taken,
                'process': form.process_name
            })

    # Prepare data for Process Steps Distribution
    steps_count = defaultdict(int)
    for form in RequirementForm.objects.filter(status='submitted'):
        if form.process_steps is not None:
            steps_count[form.process_steps] += 1

    # Convert to format for Chart.js
    steps_data = []
    for steps, count in sorted(steps_count.items()):
        steps_data.append({'x': steps, 'y': count})

    # Prepare Error Possibility data
    # error_ranges = {'0-20%': 0, '21-40%': 0, '41-60%': 0, '61-80%': 0, '81-100%': 0}
    # for form in RequirementForm.objects.filter(status='submitted'):
    #     if form.error_possibility is not None:
    #         if form.error_possibility <= 20:
    #             error_ranges['0-20%'] += 1
    #         elif form.error_possibility <= 40:
    #             error_ranges['21-40%'] += 1
    #         elif form.error_possibility <= 60:
    #             error_ranges['41-60%'] += 1
    #         elif form.error_possibility <= 80:
    #             error_ranges['61-80%'] += 1
    #         else:
    #             error_ranges['81-100%'] += 1

    # error_labels = list(error_ranges.keys())
    # error_data = list(error_ranges.values())
    
    context = {
    'question_analysis' : question_analysis,
    'total_users': total_users,
    'submitted_forms': submitted_forms,
    'response_rate': response_rate,
    'avg_completion_time': avg_completion_time,
    'chart_data': {
        'wing_labels': wing_labels,
        'wing_data': wing_data,
        'dept_labels': dept_labels,
        'dept_data': dept_data,
        'process_names': process_names_data,
        'process_counts_data': process_counts_data,
        # Add these with default values
        'time_vs_steps': [],
        'steps_data': []
        # 'error_labels': ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%'],
        # 'error_data': [0, 0, 0, 0, 0]
    },
}
    return render(request, 'requirements_app/data_analysis.html', context)

@user_passes_test(is_admin)
def download_user_list(request):
    # Generate PDF of user list
    pdf = generate_user_list_pdf()
    
    # Create HTTP response with PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="user_list.pdf"'
    
    return response

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name()}!")
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    context = {
        'form': form,
    }
    return render(request, 'requirements_app/login.html', context)


@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Process the uploaded files if they exist
            if 'photo' in request.FILES:
                # Delete old photo if exists
                if user.photo:
                    if os.path.isfile(user.photo.path):
                        os.remove(user.photo.path)
                
                user.photo = request.FILES['photo']
                
            if 'signature' in request.FILES:
                # Delete old signature if exists
                if user.signature:
                    if os.path.isfile(user.signature.path):
                        os.remove(user.signature.path)
                
                user.signature = request.FILES['signature']
            
            form.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('user_management')
    else:
        form = UserUpdateForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'requirements_app/edit_user.html', context)

@user_passes_test(is_admin)
def manage_form_structure(request):
    # Get all sections ordered by their order field
    sections = FormSection.objects.all().order_by('order')
    
    # For each section, manually add ordered questions
    for section in sections:
        section.ordered_questions = section.questions.all().order_by('order')
    
    context = {
        'sections': sections,
    }
    return render(request, 'requirements_app/manage_form_structure.html', context)

@user_passes_test(is_admin)
def edit_section(request, section_id=None):
    if section_id:
        section = get_object_or_404(FormSection, pk=section_id)
        title = f"Edit Section: {section.title}"
    else:
        section = None
        title = "Add New Section"
    
    if request.method == 'POST':
        form = FormSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, f"Section {'updated' if section else 'created'} successfully.")
            return redirect('manage_form_structure')
    else:
        form = FormSectionForm(instance=section)
    
    context = {
        'form': form,
        'title': title,
        'is_edit': section is not None,
    }
    return render(request, 'requirements_app/edit_section.html', context)

def delete_section(request, section_id):
    section = get_object_or_404(FormSection, pk=section_id)
    
    if request.method == 'POST':
        section.delete()
        messages.success(request, "Section deleted successfully.")
        return redirect('manage_form_structure')
    
    context = {
        'section': section,
    }
    return render(request, 'requirements_app/delete_section_confirm.html', context)

@user_passes_test(is_admin)
def edit_question(request, section_id, question_id=None):
    section = get_object_or_404(FormSection, pk=section_id)
    
    if question_id:
        question = get_object_or_404(FormQuestion, pk=question_id, section=section)
        title = f"Edit Question: {question.question_text}"
    else:
        question = None
        title = f"Add New Question to {section.title}"
    
    if request.method == 'POST':
        form = FormQuestionForm(request.POST, instance=question)
        if form.is_valid():
            new_question = form.save(commit=False)
            new_question.section = section
            new_question.save()
            
            messages.success(request, f"Question {'updated' if question_id else 'created'} successfully.")
            return redirect('manage_form_structure')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # For a new question, set default values
        initial_data = {}
        if not question:
            # Get the highest order value in this section and add 1
            highest_order = FormQuestion.objects.filter(section=section).order_by('-order').values_list('order', flat=True).first()
            initial_data['order'] = (highest_order or 0) + 1
            initial_data['is_active'] = True
            
        form = FormQuestionForm(instance=question, initial=initial_data)
    
    context = {
        'form': form,
        'section': section,
        'title': title,
        'is_edit': question is not None,
    }
    return render(request, 'requirements_app/edit_question.html', context)

@user_passes_test(is_admin)
def delete_question(request, question_id):
    question = get_object_or_404(FormQuestion, pk=question_id)
    section = question.section
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect('manage_form_structure')
    
    context = {
        'question': question,
        'section': section,
    }
    return render(request, 'requirements_app/delete_question_confirm.html', context)

@user_passes_test(is_admin)
def download_user_pdf(request, form_id):
    form = get_object_or_404(RequirementForm, pk=form_id)
    
    # Get all sections with questions and answers (same as view_user_form)
    sections = FormSection.objects.filter(is_active=True).order_by('order')
    sections_with_answers = []
    for section in sections:
        section_answers = []
        for question in section.questions.filter(is_active=True):
            try:
                answer = QuestionResponse.objects.get(form=form, question=question)
                section_answers.append({
                    'question': question,
                    'answer_text': answer.response_text
                })
            except QuestionResponse.DoesNotExist:
                continue
        if section_answers:
            sections_with_answers.append({
                'section': section,
                'answers': section_answers
            })

    # Generate the signature data URI
    signature_data_uri = None
    if form.user.signature:  # Check if the user has a signature
        signature_path = os.path.join(settings.MEDIA_ROOT, form.user.signature.name)
        if os.path.exists(signature_path):
            with open(signature_path, 'rb') as image_file:
                signature_data = base64.b64encode(image_file.read()).decode('utf-8')
                signature_data_uri = f"data:image/png;base64,{signature_data}"  # Adjust MIME type if needed
        else:
            print(f"Signature file not found at: {signature_path}")

    # Prepare context for the template
    context = {
        'form': form,
        'sections_with_answers': sections_with_answers,
        'user': form.user,  # Use the form's user, not the request user
        'current_date': timezone.now(),
        'signature_data_uri': signature_data_uri,
    }
    
    # Generate PDF using the utility function
    pdf = generate_pdf(form)
    
    # Create HTTP response with PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="requirement_form_{form.user.username}.pdf"'
    
    return response

@user_passes_test(is_admin)
def delete_attachment(request, form_id):
    form = get_object_or_404(RequirementForm, pk=form_id)
    
    if request.method == 'POST':
        # Check if attachment exists
        if form.attachment:
            # Delete the file from storage
            if os.path.isfile(form.attachment.path):
                os.remove(form.attachment.path)
            
            # Clear the field
            form.attachment = None
            form.save()
            
            messages.success(request, "Attachment deleted successfully.")
        else:
            messages.warning(request, "No attachment found.")
            
        return redirect('view_responses')
    
    context = {
        'form': form,
    }
    return render(request, 'requirements_app/delete_attachment_confirm.html', context)

@login_required
def delete_draft(request, form_id):
    draft = get_object_or_404(RequirementForm, id=form_id, user=request.user, status='draft')
    
    if request.method == 'POST':
        draft.delete()
        messages.success(request, "Draft form deleted successfully.")
        return redirect('dashboard')
    
    context = {
        'draft': draft,
    }
    return render(request, 'requirements_app/delete_draft_confirm.html', context)

@login_required
def review_form(request):
    # Check if there's form data in session
    if 'form_data' not in request.session or 'question_responses' not in request.session:
        messages.error(request, "No form data found for review. Please fill out the form again.")
        return redirect('form')
    
    # Get form data from session
    form_data = request.session['form_data']
    question_responses = request.session['question_responses']
    
    # Add this code to ensure process_steps_detail is properly formatted
    process_steps_detail = form_data.get('process_steps_detail', [])
    
    # For debugging
    print("Type of process_steps_detail:", type(process_steps_detail))
    print("Content of process_steps_detail:", process_steps_detail)
    
    # Ensure it's properly parsed if it's a string
    if isinstance(process_steps_detail, str):
        try:
            process_steps_detail = json.loads(process_steps_detail)
            form_data['process_steps_detail'] = process_steps_detail
        except json.JSONDecodeError:
            form_data['process_steps_detail'] = []
    
    # Create a mock form object to mimic the structure expected by the template
    form = type('obj', (object,), {
        'process_name': form_data.get('process_name', ''),
        'process_description': form_data.get('process_description', ''),
        'process_steps_detail': form_data.get('process_steps_detail', []),
        'has_flowchart': form_data.get('has_flowchart', False),
        'has_attachment': form_data.get('has_attachment', False),
        # Add other fields as needed
    })
    
    # Get active sections
    active_sections = FormSection.objects.filter(is_active=True).prefetch_related('questions').order_by('order')
    
    # Create structure for template rendering
    sections_with_answers = []
    for section in active_sections:
        section_answers = []
        
        for question in section.questions.filter(is_active=True).order_by('order'):
            # Check if we have a response for this question
            if str(question.id) in question_responses or question.id in question_responses:
                # Get answer for this question
                question_id = str(question.id) if str(question.id) in question_responses else question.id
                answer_text = question_responses[question_id]
                
                section_answers.append({
                    'question': question,
                    'answer_text': answer_text
                })
        
        # Only add sections with answers
        if section_answers:
            sections_with_answers.append({
                'section': section,
                'answers': section_answers
            })
    
    context = {
        'form_data': form_data,
        'form': form,  # Add this to provide the template with the expected structure
        'sections_with_answers': sections_with_answers
    }
    
    return render(request, 'requirements_app/review_form.html', context)

@login_required
def edit_form(request):
    # Check if user came from review page
    if 'form_data' not in request.session:
        messages.error(request, "No form data found. Please fill out the form again.")
        return redirect('form')
    
    # Get form_id if we're editing an existing draft
    form_id = request.session['form_data'].get('form_id')
    
    # Redirect back to form page
    if form_id:
        return redirect('form_view', form_id=form_id)
    else:
        return redirect('form')

@login_required
def confirm_submission(request):
    # Check if user came from review page
    if 'form_data' not in request.session or 'question_responses' not in request.session:
        messages.error(request, "No form data found. Please fill out the form again.")
        return redirect('form')
    
    if request.method != 'POST':
        return redirect('review_form')
    
    # Get data from session
    form_data = request.session['form_data']
    question_responses = request.session['question_responses']
    temp_files = request.session.get('temp_files', {})
    
    # Get or create form instance
    form_id = form_data.get('form_id')
    if form_id:
        form_instance = get_object_or_404(RequirementForm, id=form_id, user=request.user, status='draft')
    else:
        form_instance = RequirementForm(user=request.user)
    
    # Update form instance with data from form_data
    for field, value in form_data.items():
        if field in ['form_id', 'has_flowchart', 'has_attachment']:
            continue
        setattr(form_instance, field, value)
    
    # Set status to submitted and save timestamp
    form_instance.status = 'submitted'
    form_instance.submitted_at = timezone.now()
    
    # Handle file uploads from temp files
    if 'flowchart' in temp_files:
        with open(temp_files['flowchart'], 'rb') as f:
            content = f.read()
            filename = f"{request.user.username}_DataFlow.pdf"
            form_instance.flowchart.save(filename, ContentFile(content), save=False)
    
    if 'attachment' in temp_files:
        with open(temp_files['attachment'], 'rb') as f:
            content = f.read()
            filename = f"{request.user.username}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
            form_instance.attachment.save(filename, ContentFile(content), save=False)
    
    # Save the form
    form_instance.save()
    
    # Save question responses
    for question_id, answer_text in question_responses.items():
        try:
            question = FormQuestion.objects.get(id=int(question_id))
            QuestionResponse.objects.update_or_create(
                form=form_instance,
                question=question,
                defaults={'response_text': answer_text}
            )
        except (FormQuestion.DoesNotExist, ValueError):
            continue
    
    # Clean up temp files
    for temp_path in temp_files.values():
        try:
            os.unlink(temp_path)
        except (OSError, IOError):
            pass
    
    # Clean up session
    for key in ['form_data', 'question_responses', 'temp_files', 'review_timestamp']:
        if key in request.session:
            del request.session[key]
    
    # Show success message
    messages.success(request, "Form submitted successfully!")
    
    # Redirect to view submission page
    return redirect('view_submissions')

@user_passes_test(is_admin)
def reports(request):
    """View for displaying the reports page"""
    # Get all unique wings and departments for filtering
    wings = User.objects.values('wing_name').distinct().exclude(wing_name='').order_by('wing_name')
    departments = User.objects.values('department_name').distinct().exclude(department_name='').order_by('department_name')
    
    # Get all users for the form submissions report
    users = User.objects.filter(role='user').order_by('username')
    
    # Get all unique process names for the process report
    processes = RequirementForm.objects.filter(status='submitted') \
                                .values('process_name') \
                                .distinct() \
                                .exclude(process_name='') \
                                .order_by('process_name')
    
    context = {
        'wings': wings,
        'departments': departments,
        'users': users,
        'processes': processes,
    }
    
    return render(request, 'requirements_app/reports.html', context)

@user_passes_test(is_admin)
def preview_report(request):
    """View for generating preview data for reports"""
    report_type = request.GET.get('report_type')
    
    try:
        if report_type == 'all-users':
            return preview_all_users_report(request)
        elif report_type == 'regular-users':
            return preview_regular_users_report(request)
        elif report_type == 'admin-users':
            return preview_admin_users_report(request)
        elif report_type == 'submitted-forms':
            return preview_submitted_forms_report(request)
        elif report_type == 'wing-forms':
            return preview_wing_forms_report(request)
        elif report_type == 'form-submissions':
            return preview_form_submissions_report(request)
        elif report_type == 'department-forms':
            return preview_department_forms_report(request)
        elif report_type == 'process-forms':
            return preview_process_forms_report(request)
        else:
            return JsonResponse({'error': 'Invalid report type'})
    except Exception as e:
        return JsonResponse({'error': str(e)})

def preview_all_users_report(request):
    """Generate preview data for all users report"""
    # Get filter parameters
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    department = request.GET.get('department', '')
    
    # Base query
    query = User.objects.all().order_by('username')
    
    # Apply filters
    if search:
        query = query.filter(
            Q(username__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search)
        )
    
    if wing:
        query = query.filter(wing_name=wing)
    
    if department:
        query = query.filter(department_name=department)
    
    # Limit to 50 users for preview
    query = query[:50]
    
    # Generate HTML rows
    rows = []
    for user in query:
        row = f"""
        <td>{user.username}</td>
        <td>{user.get_full_name()}</td>
        <td>{user.get_role_display()}</td>
        <td>{user.designation}</td>
        <td>{user.wing_name}</td>
        <td>{user.department_name}</td>
        """
        rows.append(row)
    
    return JsonResponse({
        'rows': rows,
        'count': len(rows),
        'total': User.objects.count()
    })

def preview_regular_users_report(request):
    """Generate preview data for regular users report"""
    # Get filter parameters
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    department = request.GET.get('department', '')
    
    # Base query for regular users only
    query = User.objects.filter(role='user').order_by('username')
    
    # Apply filters
    if search:
        query = query.filter(
            Q(username__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search)
        )
    
    if wing:
        query = query.filter(wing_name=wing)
    
    if department:
        query = query.filter(department_name=department)
    
    # Limit to 50 users for preview
    query = query[:50]
    
    # Generate HTML rows
    rows = []
    for user in query:
        row = f"""
        <td>{user.username}</td>
        <td>{user.get_full_name()}</td>
        <td>{user.designation}</td>
        <td>{user.wing_name}</td>
        <td>{user.department_name}</td>
        <td>{user.mobile}</td>
        """
        rows.append(row)
    
    return JsonResponse({
        'rows': rows,
        'count': len(rows),
        'total': User.objects.filter(role='user').count()
    })

def preview_admin_users_report(request):
    """Generate preview data for admin users report"""
    # Get filter parameters
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    
    # Base query for admin users only
    query = User.objects.filter(role='admin').order_by('username')
    
    # Apply filters
    if search:
        query = query.filter(
            Q(username__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search)
        )
    
    if wing:
        query = query.filter(wing_name=wing)
    
    # Limit to 50 users for preview
    query = query[:50]
    
    # Generate HTML rows
    rows = []
    for user in query:
        row = f"""
        <td>{user.username}</td>
        <td>{user.get_full_name()}</td>
        <td>{user.designation}</td>
        <td>{user.wing_name}</td>
        <td>{user.department_name}</td>
        <td>{user.mobile}</td>
        """
        rows.append(row)
    
    return JsonResponse({
        'rows': rows,
        'count': len(rows),
        'total': User.objects.filter(role='admin').count()
    })

def preview_submitted_forms_report(request):
    """Generate preview data for submitted forms report"""
    # Get filter parameters
    user_id = request.GET.get('user', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base query for submitted forms
    query = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    # Apply filters
    if user_id:
        query = query.filter(user_id=user_id)
    
    if process:
        query = query.filter(process_name__icontains=process)
    
    if date_from:
        query = query.filter(submitted_at__gte=date_from)
    
    if date_to:
        query = query.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Limit to 50 forms for preview
    query = query[:50]
    
    # Generate HTML rows
    rows = []
    for form in query:
        submitted_at = form.submitted_at.strftime('%Y-%m-%d %H:%M') if form.submitted_at else 'N/A'
        row = f"""
        <td>{form.user.username}</td>
        <td>{form.user.get_full_name()}</td>
        <td>{form.process_name}</td>
        <td>{submitted_at}</td>
        <td>{form.user.wing_name}</td>
        <td>{form.user.department_name}</td>
        """
        rows.append(row)
    
    return JsonResponse({
        'rows': rows,
        'count': len(rows),
        'total': RequirementForm.objects.filter(status='submitted').count()
    })

def preview_wing_forms_report(request):
    """Generate preview data for wing-wise forms report"""
    # Get filter parameters
    wing = request.GET.get('wing', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not wing:
        return JsonResponse({
            'error': 'Please select a wing',
            'rows': [],
            'count': 0
        })
    
    # Base query for submitted forms in the selected wing
    query = RequirementForm.objects.filter(
        status='submitted',
        user__wing_name=wing
    ).order_by('-submitted_at')
    
    # Apply additional filters
    if process:
        query = query.filter(process_name__icontains=process)
    
    if date_from:
        query = query.filter(submitted_at__gte=date_from)
    
    if date_to:
        query = query.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Limit to 50 forms for preview
    query = query[:50]
    
    # Generate HTML rows
    rows = []
    for form in query:
        submitted_at = form.submitted_at.strftime('%Y-%m-%d %H:%M') if form.submitted_at else 'N/A'
        row = f"""
        <td>{wing}</td>
        <td>{form.user.username}</td>
        <td>{form.user.get_full_name()}</td>
        <td>{form.process_name}</td>
        <td>{submitted_at}</td>
        <td>{form.user.department_name}</td>
        """
        rows.append(row)
    
    return JsonResponse({
        'rows': rows,
        'count': len(rows),
        'total': RequirementForm.objects.filter(status='submitted', user__wing_name=wing).count()
    })

def preview_form_submissions_report(request):
    """Generate preview data for form submissions report"""
    # Get filter parameters
    user_selection = request.GET.get('user_selection', 'all')
    specific_user = request.GET.get('specific_user', '')
    selected_users = request.GET.get('selected_users', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base query for submitted forms
    query = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    # Apply user filters based on selection type
    if user_selection == 'specific' and specific_user:
        query = query.filter(user_id=specific_user)
    elif user_selection == 'multiple' and selected_users:
        user_ids = selected_users.split(',')
        query = query.filter(user_id__in=user_ids)
    
    # Apply other filters
    if process:
        query = query.filter(process_name__icontains=process)
    
    if date_from:
        query = query.filter(submitted_at__gte=date_from)
    
    if date_to:
        query = query.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Limit to 50 forms for preview
    query = query[:50]
    
    # Generate HTML rows
    rows = []
    for form in query:
        submitted_at = form.submitted_at.strftime('%Y-%m-%d %H:%M') if form.submitted_at else 'N/A'
        row = f"""
        <td>{form.user.username}</td>
        <td>{form.user.get_full_name()}</td>
        <td>{form.process_name}</td>
        <td>{submitted_at}</td>
        <td>{form.user.wing_name}</td>
        <td>{form.user.department_name}</td>
        """
        rows.append(row)
    
    return JsonResponse({
        'rows': rows,
        'count': len(rows)
    })

def preview_department_forms_report(request):
    """Generate preview data for department-wise forms report"""
    # Get filter parameters
    department = request.GET.get('department', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not department:
        return JsonResponse({
            'error': 'Please select a department',
            'rows': [],
            'count': 0
        })
    
    # Base query for submitted forms in the selected department
    query = RequirementForm.objects.filter(
        status='submitted',
        user__department_name=department
    ).order_by('-submitted_at')
    
    # Apply additional filters
    if process:
        query = query.filter(process_name__icontains=process)
    
    if date_from:
        query = query.filter(submitted_at__gte=date_from)
    
    if date_to:
        query = query.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Limit to 50 forms for preview
    query = query[:50]
    
    # Generate HTML rows
    rows = []
    for form in query:
        submitted_at = form.submitted_at.strftime('%Y-%m-%d %H:%M') if form.submitted_at else 'N/A'
        row = f"""
        <td>{department}</td>
        <td>{form.user.username}</td>
        <td>{form.user.get_full_name()}</td>
        <td>{form.process_name}</td>
        <td>{submitted_at}</td>
        <td>{form.user.wing_name}</td>
        """
        rows.append(row)
    
    return JsonResponse({
        'rows': rows,
        'count': len(rows),
        'total': RequirementForm.objects.filter(status='submitted', user__department_name=department).count()
    })

def preview_process_forms_report(request):
    """Generate preview data for process-wise forms report"""
    # Get filter parameters
    process = request.GET.get('process', '')
    wing = request.GET.get('wing', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not process:
        return JsonResponse({
            'error': 'Please select a process',
            'rows': [],
            'count': 0
        })
    
    # Base query for submitted forms with the selected process
    query = RequirementForm.objects.filter(
        status='submitted',
        process_name=process
    ).order_by('-submitted_at')
    
    # Apply additional filters
    if wing:
        query = query.filter(user__wing_name=wing)
    
    if date_from:
        query = query.filter(submitted_at__gte=date_from)
    
    if date_to:
        query = query.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Limit to 50 forms for preview
    query = query[:50]
    
    # Generate HTML rows
    rows = []
    for form in query:
        submitted_at = form.submitted_at.strftime('%Y-%m-%d %H:%M') if form.submitted_at else 'N/A'
        row = f"""
        <td>{process}</td>
        <td>{form.user.username}</td>
        <td>{form.user.get_full_name()}</td>
        <td>{submitted_at}</td>
        <td>{form.user.wing_name}</td>
        <td>{form.user.department_name}</td>
        """
        rows.append(row)
    
    return JsonResponse({
        'rows': rows,
        'count': len(rows),
        'total': RequirementForm.objects.filter(status='submitted', process_name=process).count()
    })

@user_passes_test(is_admin)
def generate_report(request):
    """Generate PDF report based on type and filters"""
    report_type = request.GET.get('report_type')
    
    try:
        if report_type == 'all-users':
            return generate_all_users_report(request)
        elif report_type == 'regular-users':
            return generate_regular_users_report(request)
        elif report_type == 'admin-users':
            return generate_admin_users_report(request)
        elif report_type == 'submitted-forms':
            return generate_submitted_forms_report(request)
        elif report_type == 'wing-forms':
            return generate_wing_forms_report(request)
        elif report_type == 'form-submissions':
            return generate_form_submissions_report(request)
        elif report_type == 'department-forms':
            return generate_department_forms_report(request)
        elif report_type == 'process-forms':
            return generate_process_forms_report(request)
        else:
            messages.error(request, 'Invalid report type')
            return redirect('reports')
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('reports')

def preview_all_users_report(request):
    """Preview data for all users report"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    department = request.GET.get('department', '')
    
    # Query users with filters
    users = User.objects.all().order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    if department:
        users = users.filter(department_name=department)
    
    # Limit to preview size
    users = users[:25]
    
    # Format rows for table
    rows = []
    for user in users:
        rows.append(
            f'<td>{user.username}</td>' +
            f'<td>{user.get_full_name()}</td>' +
            f'<td>{user.get_role_display()}</td>' +
            f'<td>{user.designation}</td>' +
            f'<td>{user.wing_name}</td>' +
            f'<td>{user.department_name}</td>'
        )
    
    return JsonResponse({'rows': rows})

def preview_regular_users_report(request):
    """Preview data for regular users report"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    department = request.GET.get('department', '')
    
    # Query regular users with filters
    users = User.objects.filter(role='user').order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    if department:
        users = users.filter(department_name=department)
    
    # Limit to preview size
    users = users[:25]
    
    # Format rows for table
    rows = []
    for user in users:
        rows.append(
            f'<td>{user.username}</td>' +
            f'<td>{user.get_full_name()}</td>' +
            f'<td>{user.designation}</td>' +
            f'<td>{user.wing_name}</td>' +
            f'<td>{user.department_name}</td>' +
            f'<td>{user.mobile}</td>'
        )
    
    return JsonResponse({'rows': rows})

def preview_admin_users_report(request):
    """Preview data for admin users report"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    
    # Query admin users with filters
    users = User.objects.filter(role='admin').order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    
    # Limit to preview size
    users = users[:25]
    
    # Format rows for table
    rows = []
    for user in users:
        rows.append(
            f'<td>{user.username}</td>' +
            f'<td>{user.get_full_name()}</td>' +
            f'<td>{user.designation}</td>' +
            f'<td>{user.wing_name}</td>' +
            f'<td>{user.department_name}</td>' +
            f'<td>{user.mobile}</td>'
        )
    
    return JsonResponse({'rows': rows})

def preview_submitted_forms_report(request):
    """Preview data for submitted forms report"""
    user_id = request.GET.get('user', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Query submitted forms with filters
    forms = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    if user_id:
        forms = forms.filter(user_id=user_id)
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Limit to preview size
    forms = forms[:25]
    
    # Format rows for table
    rows = []
    for form in forms:
        rows.append(
            f'<td>{form.user.username}</td>' +
            f'<td>{form.user.get_full_name()}</td>' +
            f'<td>{form.process_name}</td>' +
            f'<td>{form.submitted_at.strftime("%Y-%m-%d %H:%M")}</td>' +
            f'<td>{form.user.wing_name}</td>' +
            f'<td>{form.user.department_name}</td>'
        )
    
    return JsonResponse({'rows': rows})

def preview_wing_forms_report(request):
    """Preview data for wing-wise forms report"""
    wing = request.GET.get('wing', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not wing:
        return JsonResponse({'error': 'Wing selection is required'})
    
    # Query submitted forms for this wing with filters
    forms = RequirementForm.objects.filter(status='submitted', user__wing_name=wing).order_by('-submitted_at')
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Limit to preview size
    forms = forms[:25]
    
    # Format rows for table
    rows = []
    for form in forms:
        rows.append(
            f'<td>{form.user.wing_name}</td>' +
            f'<td>{form.user.username}</td>' +
            f'<td>{form.user.get_full_name()}</td>' +
            f'<td>{form.process_name}</td>' +
            f'<td>{form.submitted_at.strftime("%Y-%m-%d %H:%M")}</td>' +
            f'<td>{form.user.department_name}</td>'
        )
    
    return JsonResponse({'rows': rows})

def preview_form_submissions_report(request):
    """Preview data for form submissions report"""
    user_selection = request.GET.get('user_selection', 'all')
    specific_user = request.GET.get('specific_user', '')
    selected_users = request.GET.get('selected_users', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    process = request.GET.get('process', '')
    
    # Query submitted forms based on user selection
    forms = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    if user_selection == 'specific' and specific_user:
        forms = forms.filter(user_id=specific_user)
    elif user_selection == 'multiple' and selected_users:
        user_ids = selected_users.split(',')
        forms = forms.filter(user_id__in=user_ids)
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Limit to preview size
    forms = forms[:25]
    
    # Format rows for table
    rows = []
    for form in forms:
        rows.append(
            f'<td>{form.user.username}</td>' +
            f'<td>{form.user.get_full_name()}</td>' +
            f'<td>{form.process_name}</td>' +
            f'<td>{form.submitted_at.strftime("%Y-%m-%d %H:%M")}</td>' +
            f'<td>{form.user.wing_name}</td>' +
            f'<td>{form.user.department_name}</td>'
        )
    
    return JsonResponse({'rows': rows})

def preview_department_forms_report(request):
    """Preview data for department-wise forms report"""
    department = request.GET.get('department', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not department:
        return JsonResponse({'error': 'Department selection is required'})
    
    # Query submitted forms for this department with filters
    forms = RequirementForm.objects.filter(status='submitted', user__department_name=department).order_by('-submitted_at')
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Limit to preview size
    forms = forms[:25]
    
    # Format rows for table
    rows = []
    for form in forms:
        rows.append(
            f'<td>{form.user.department_name}</td>' +
            f'<td>{form.user.username}</td>' +
            f'<td>{form.user.get_full_name()}</td>' +
            f'<td>{form.process_name}</td>' +
            f'<td>{form.submitted_at.strftime("%Y-%m-%d %H:%M")}</td>' +
            f'<td>{form.user.wing_name}</td>'
        )
    
    return JsonResponse({'rows': rows})

def preview_process_forms_report(request):
    """Preview data for process-wise forms report"""
    process = request.GET.get('process', '')
    wing = request.GET.get('wing', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not process:
        return JsonResponse({'error': 'Process selection is required'})
    
    # Query submitted forms for this process with filters
    forms = RequirementForm.objects.filter(status='submitted', process_name=process).order_by('-submitted_at')
    
    if wing:
        forms = forms.filter(user__wing_name=wing)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Limit to preview size
    forms = forms[:25]
    
    # Format rows for table
    rows = []
    for form in forms:
        rows.append(
            f'<td>{form.process_name}</td>' +
            f'<td>{form.user.username}</td>' +
            f'<td>{form.user.get_full_name()}</td>' +
            f'<td>{form.submitted_at.strftime("%Y-%m-%d %H:%M")}</td>' +
            f'<td>{form.user.wing_name}</td>' +
            f'<td>{form.user.department_name}</td>'
        )
    
    return JsonResponse({'rows': rows})

def generate_all_users_pdf(request):
    """Generate PDF report for all users"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    department = request.GET.get('department', '')
    
    # Query users with filters
    users = User.objects.all().order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    if department:
        users = users.filter(department_name=department)
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'users': users,
        'report_title': 'All Users Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'search': search,
            'wing': wing,
            'department': department
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/users_report_template.html', 
        context, 
        filename="all_users_report.pdf"
    )

def generate_regular_users_pdf(request):
    """Generate PDF report for regular users"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    department = request.GET.get('department', '')
    
    # Query regular users with filters
    users = User.objects.filter(role='user').order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    if department:
        users = users.filter(department_name=department)
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'users': users,
        'report_title': 'Regular Users Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'search': search,
            'wing': wing,
            'department': department
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/users_report_template.html', 
        context, 
        filename="regular_users_report.pdf"
    )

def generate_admin_users_pdf(request):
    """Generate PDF report for admin users"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    
    # Query admin users with filters
    users = User.objects.filter(role='admin').order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'users': users,
        'report_title': 'Admin Users Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'search': search,
            'wing': wing
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/users_report_template.html', 
        context, 
        filename="admin_users_report.pdf"
    )

def generate_submitted_forms_pdf(request):
    """Generate PDF report for submitted forms"""
    user_id = request.GET.get('user', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Query submitted forms with filters
    forms = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    if user_id:
        forms = forms.filter(user_id=user_id)
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': 'Submitted Forms Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'user': User.objects.get(id=user_id).username if user_id else 'All',
            'process': process,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/forms_report_template.html', 
        context, 
        filename="submitted_forms_report.pdf"
    )

def generate_wing_forms_pdf(request):
    """Generate PDF report for wing-wise forms"""
    wing = request.GET.get('wing', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not wing:
        messages.error(request, "Wing selection is required")
        return redirect('reports')
    
    # Query submitted forms for this wing with filters
    forms = RequirementForm.objects.filter(status='submitted', user__wing_name=wing).order_by('-submitted_at')
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': f'{wing} Wing Forms Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'wing': wing,
            'process': process,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/wing_forms_report_template.html', 
        context, 
        filename=f"{wing}_wing_forms_report.pdf"
    )

def generate_form_submissions_pdf(request):
    """Generate PDF report for form submissions"""
    user_selection = request.GET.get('user_selection', 'all')
    specific_user = request.GET.get('specific_user', '')
    selected_users = request.GET.get('selected_users', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    process = request.GET.get('process', '')
    
    # Query submitted forms based on user selection
    forms = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    if user_selection == 'specific' and specific_user:
        forms = forms.filter(user_id=specific_user)
    elif user_selection == 'multiple' and selected_users:
        user_ids = selected_users.split(',')
        forms = forms.filter(user_id__in=user_ids)
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': 'Form Submissions Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'user_selection': user_selection,
            'process': process,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/forms_report_template.html', 
        context, 
        filename="form_submissions_report.pdf"
    )

def generate_department_forms_pdf(request):
    """Generate PDF report for department-wise forms"""
    department = request.GET.get('department', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not department:
        messages.error(request, "Department selection is required")
        return redirect('reports')
    
    # Query submitted forms for this department with filters
    forms = RequirementForm.objects.filter(status='submitted', user__department_name=department).order_by('-submitted_at')
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': f'{department} Department Forms Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'department': department,
            'process': process,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/department_forms_report_template.html', 
        context, 
        filename=f"{department}_department_forms_report.pdf"
    )

def generate_process_forms_pdf(request):
    """Generate PDF report for process-wise forms"""
    process = request.GET.get('process', '')
    wing = request.GET.get('wing', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not process:
        messages.error(request, "Process selection is required")
        return redirect('reports')
    
    # Query submitted forms for this process with filters
    forms = RequirementForm.objects.filter(status='submitted', process_name=process).order_by('-submitted_at')
    
    if wing:
        forms = forms.filter(user__wing_name=wing)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to)
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': f'{process} Process Forms Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'process': process,
            'wing': wing,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/process_forms_report_template.html', 
        context, 
        filename=f"{process}_process_forms_report.pdf"
    )

@user_passes_test(is_admin)
def generate_all_users_report(request):
    """Generate PDF report for all users"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    department = request.GET.get('department', '')
    
    # Query users with filters
    users = User.objects.all().order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    if department:
        users = users.filter(department_name=department)
    
    # Get logo as data URI
    from .utils import get_static_file_as_data_uri
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'users': users,
        'report_title': 'All Users Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'search': search,
            'wing': wing,
            'department': department
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/users_report_template.html', 
        context, 
        filename="all_users_report.pdf"
    )

@user_passes_test(is_admin)
def generate_regular_users_report(request):
    """Generate PDF report for regular users"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    department = request.GET.get('department', '')
    
    # Query regular users with filters
    users = User.objects.filter(role='user').order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    if department:
        users = users.filter(department_name=department)
    
    # Get logo as data URI
    from .utils import get_static_file_as_data_uri
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'users': users,
        'report_title': 'Regular Users Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'search': search,
            'wing': wing,
            'department': department
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/users_report_template.html', 
        context, 
        filename="regular_users_report.pdf"
    )

@user_passes_test(is_admin)
def generate_admin_users_report(request):
    """Generate PDF report for admin users"""
    search = request.GET.get('search', '')
    wing = request.GET.get('wing', '')
    
    # Query admin users with filters
    users = User.objects.filter(role='admin').order_by('username')
    
    if search:
        users = users.filter(Q(username__icontains=search) | 
                            Q(first_name__icontains=search) | 
                            Q(last_name__icontains=search))
    if wing:
        users = users.filter(wing_name=wing)
    
    # Get logo as data URI
    from .utils import get_static_file_as_data_uri
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'users': users,
        'report_title': 'Admin Users Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'search': search,
            'wing': wing
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/users_report_template.html', 
        context, 
        filename="admin_users_report.pdf"
    )

@user_passes_test(is_admin)
def generate_submitted_forms_report(request):
    """Generate PDF report for submitted forms"""
    user_id = request.GET.get('user', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Query submitted forms with filters
    forms = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    if user_id:
        forms = forms.filter(user_id=user_id)
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Get logo as data URI
    from .utils import get_static_file_as_data_uri
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare user name for filter display
    username = 'All'
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            username = user.username
        except User.DoesNotExist:
            pass
            
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': 'Submitted Forms Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'user': username,
            'process': process,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/forms_report_template.html', 
        context, 
        filename="submitted_forms_report.pdf"
    )

@user_passes_test(is_admin)
def generate_wing_forms_report(request):
    """Generate PDF report for wing-wise forms"""
    wing = request.GET.get('wing', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not wing:
        messages.error(request, "Wing selection is required")
        return redirect('reports')
    
    # Query submitted forms for this wing with filters
    forms = RequirementForm.objects.filter(status='submitted', user__wing_name=wing).order_by('-submitted_at')
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Get logo as data URI
    from .utils import get_static_file_as_data_uri
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': f'{wing} Wing Forms Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'wing': wing,
            'process': process,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/wing_forms_report_template.html', 
        context, 
        filename=f"{wing}_wing_forms_report.pdf"
    )

@user_passes_test(is_admin)
def generate_form_submissions_report(request):
    """Generate PDF report for form submissions"""
    user_selection = request.GET.get('user_selection', 'all')
    specific_user = request.GET.get('specific_user', '')
    selected_users = request.GET.get('selected_users', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    process = request.GET.get('process', '')
    
    # Query submitted forms based on user selection
    forms = RequirementForm.objects.filter(status='submitted').order_by('-submitted_at')
    
    if user_selection == 'specific' and specific_user:
        forms = forms.filter(user_id=specific_user)
    elif user_selection == 'multiple' and selected_users:
        user_ids = selected_users.split(',')
        forms = forms.filter(user_id__in=user_ids)
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Get logo as data URI
    from .utils import get_static_file_as_data_uri
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': 'Form Submissions Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'user_selection': user_selection,
            'process': process,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/forms_report_template.html', 
        context, 
        filename="form_submissions_report.pdf"
    )

@user_passes_test(is_admin)
def generate_department_forms_report(request):
    """Generate PDF report for department-wise forms"""
    department = request.GET.get('department', '')
    process = request.GET.get('process', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not department:
        messages.error(request, "Department selection is required")
        return redirect('reports')
    
    # Query submitted forms for this department with filters
    forms = RequirementForm.objects.filter(status='submitted', user__department_name=department).order_by('-submitted_at')
    
    if process:
        forms = forms.filter(process_name__icontains=process)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Get logo as data URI
    from .utils import get_static_file_as_data_uri
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': f'{department} Department Forms Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'department': department,
            'process': process,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/department_forms_report_template.html', 
        context, 
        filename=f"{department}_department_forms_report.pdf"
    )

@user_passes_test(is_admin)
def generate_process_forms_report(request):
    """Generate PDF report for process-wise forms"""
    process = request.GET.get('process', '')
    wing = request.GET.get('wing', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if not process:
        messages.error(request, "Process selection is required")
        return redirect('reports')
    
    # Query submitted forms for this process with filters
    forms = RequirementForm.objects.filter(status='submitted', process_name=process).order_by('-submitted_at')
    
    if wing:
        forms = forms.filter(user__wing_name=wing)
    if date_from:
        forms = forms.filter(submitted_at__gte=date_from)
    if date_to:
        forms = forms.filter(submitted_at__lte=date_to + ' 23:59:59')
    
    # Get logo as data URI
    from .utils import get_static_file_as_data_uri
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Prepare context data
    context = {
        'forms': forms,
        'report_title': f'{process} Process Forms Report',
        'logo_data_uri': logo_data_uri,
        'current_date': timezone.now(),
        'filters': {
            'process': process,
            'wing': wing,
            'date_from': date_from,
            'date_to': date_to
        }
    }
    
    # Generate PDF
    return generate_report_pdf(
        'requirements_app/pdf/process_forms_report_template.html', 
        context, 
        filename=f"{process}_process_forms_report.pdf"
    )

def generate_report_pdf(template_path, context, filename="report.pdf"):
    """Generate PDF report from a template and context data"""
    # Render HTML string from template
    html_string = render_to_string(template_path, context)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output:
        # Generate PDF
        HTML(string=html_string).write_pdf(
            output,
            stylesheets=[
                CSS(string='@page { size: A4; margin: 1cm }')
            ]
        )
        output_path = output.name
    
    # Read the generated PDF
    with open(output_path, 'rb') as f:
        pdf_content = f.read()
    
    # Clean up the temporary file
    os.unlink(output_path)
    
    # Create HTTP response with PDF
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@user_passes_test(is_admin)
def edit_submitted_form(request, form_id):
    # Get the form instance
    form_instance = get_object_or_404(RequirementForm, pk=form_id, status='submitted')
    
    # Get all active form sections with their questions
    active_sections = FormSection.objects.filter(is_active=True).prefetch_related('questions').order_by('order')

    if request.method == 'POST':
        # Process the basic form data
        basic_form = RequirementFormForm(request.POST, request.FILES, instance=form_instance)
        # Process the dynamic questions
        dynamic_form = DynamicForm(request.POST, sections=active_sections, instance=form_instance)

        if basic_form.is_valid() and dynamic_form.is_valid():
            # Save the basic form
            requirement_form = basic_form.save(commit=False)
            
            # Handle file uploads
            if 'attachment' in request.FILES:
                file = request.FILES['attachment']
                if file.name.endswith('.pdf'):
                    filename = f"{form_instance.user.username}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
                    content = file.read()
                    requirement_form.attachment.save(filename, ContentFile(content), save=False)
                else:
                    messages.error(request, "Attachment must be a PDF file.")
                    return redirect('edit_submitted_form', form_id=form_id)
                    
            # Handle flowchart upload (if provided)
            if 'flowchart' in request.FILES:
                file = request.FILES['flowchart']
                if file.name.endswith('.pdf'):
                    # Model will handle filename with custom upload path
                    pass
                else:
                    messages.error(request, "Flowchart must be a PDF file.")
                    return redirect('edit_submitted_form', form_id=form_id)
            
            # Save the form
            requirement_form.updated_at = timezone.now()
            requirement_form.save()

            # Save responses for dynamic questions
            for field_name, value in dynamic_form.cleaned_data.items():
                if field_name.startswith('question_'):
                    question_id = int(field_name.split('_')[1])
                    question = FormQuestion.objects.get(id=question_id)

                    # Convert list values to string for checkboxes
                    if isinstance(value, list):
                        value = ', '.join(value)

                    # Create or update response
                    QuestionResponse.objects.update_or_create(
                        form=requirement_form,
                        question=question,
                        defaults={'response_text': value if value is not None else ''}
                    )

            messages.success(request, "Form updated successfully.")
            return redirect('view_responses')
        else:
            # If forms are invalid, display errors
            for field, errors in basic_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

            for field, errors in dynamic_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        # Initial form load
        basic_form = RequirementFormForm(instance=form_instance)
        dynamic_form = DynamicForm(sections=active_sections, instance=form_instance)
        
    # Group questions by section (same as in form_view)
    sections_with_questions = []
    for section in active_sections:
        questions = []
        for question in section.questions.filter(is_active=True).order_by('order'):
            field_name = f"question_{question.id}"
            if field_name in dynamic_form.fields:
                questions.append({
                    'question': question,
                    'field': dynamic_form[field_name]
                })

        if questions:  # Only add sections with active questions
            sections_with_questions.append({
                'section': section,
                'questions': questions
            })

    context = {
        'basic_form': basic_form,
        'dynamic_form': dynamic_form,
        'sections_with_questions': sections_with_questions,
        'form_instance': form_instance,
        'form_id': form_id,
    }

    return render(request, 'requirements_app/edit_submitted_form.html', context)