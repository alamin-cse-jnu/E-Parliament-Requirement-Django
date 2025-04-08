from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import User, RequirementForm, FormSection, FormQuestion, QuestionResponse
from .forms import RequirementFormForm, UserRegistrationForm, UserUpdateForm, DynamicForm, FormQuestionForm, FormSectionForm
from .utils import generate_pdf, generate_user_list_pdf
import json
from django.db.models import Count, Avg, Q
from collections import defaultdict
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from .forms import LoginForm  
import os
import base64
from django.conf import settings

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    
    user_form = RequirementForm.objects.filter(user=request.user).first()
    
    context = {
        'user_form': user_form,
    }
    return render(request, 'requirements_app/dashboard.html', context)

@login_required
def form_view(request):
    # Get existing form instance or None
    instance = RequirementForm.objects.filter(user=request.user).first()
    if instance and instance.status == 'submitted':
        messages.warning(request, "You have already submitted the form. Contact admin if you need to make changes.")
        return redirect('view_form')

    # Get all active form sections with their questions
    active_sections = FormSection.objects.filter(is_active=True).prefetch_related('questions').order_by('order')

    if request.method == 'POST':
        # Process the basic form data
        basic_form = RequirementFormForm(request.POST, request.FILES, instance=instance)
        # Process the dynamic questions
        dynamic_form = DynamicForm(request.POST, sections=active_sections, instance=instance)

        if basic_form.is_valid() and dynamic_form.is_valid():
            # Save the basic form
            requirement_form = basic_form.save(commit=False)
            requirement_form.user = request.user

            # Handle file upload
            if 'attachment' in request.FILES:
                file = request.FILES['attachment']
                if file.name.endswith('.pdf'):
                    filename = f"{request.user.username}.pdf"
                    # requirement_form.save()  # Save to get ID
                    # requirement_form.attachment.save(filename, file)
                    # Create a new file with the custom name
                    from django.core.files.base import ContentFile
                    content = file.read()
                    requirement_form.attachment.save(filename, ContentFile(content), save=False)
                    # The save=False parameter tells Django not to save the model instance
                else:
                    messages.error(request, "Attachment must be a PDF file.")
                    requirement_form.attachment = None
                    return redirect('form_view')

            # Set status based on button clicked
            if 'save_draft' in request.POST:
                requirement_form.status = 'draft'
            elif 'submit' in request.POST:
                requirement_form.status = 'submitted'
                requirement_form.submitted_at = timezone.now()

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

            # Provide feedback and redirect based on button
            if 'save_draft' in request.POST:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Form saved as draft successfully.'})
                messages.success(request, "Form saved as draft successfully.")
                return redirect('dashboard')
            elif 'submit' in request.POST:
                messages.success(request, "Form submitted successfully.")
                return redirect('view_form')

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
        'is_draft': instance and instance.status == 'draft',
    }

    return render(request, 'requirements_app/form.html', context)



@login_required
def view_form(request):
    form = get_object_or_404(RequirementForm, user=request.user)
    
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
def download_pdf(request):
    form = get_object_or_404(RequirementForm, user=request.user)
    
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
    response['Content-Disposition'] = f'attachment; filename="requirement_form_{request.user.username}.pdf"'
    
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
    # Process type analysis (using current_process field)
    process_data = RequirementForm.objects.filter(status='submitted').values('current_process').annotate(count=Count('current_process'))
    
    # Prepare process chart data
    process_labels = [item['current_process'] for item in process_data]
    process_counts = [item['count'] for item in process_data]

    # Example: Analyze responses to specific dynamic questions
    # Let's assume some questions relate to time, employees, or errors
    # Replace these with actual question IDs or texts from your FormQuestion model
    time_question = FormQuestion.objects.filter(question_text__icontains='time').first()
    employee_question = FormQuestion.objects.filter(question_text__icontains='employee').first()
    error_question = FormQuestion.objects.filter(question_text__icontains='error').first()

    # Aggregate responses for these questions
    time_responses = defaultdict(int)
    employee_responses = defaultdict(int)
    error_responses = defaultdict(int)

    if time_question:
        time_data = QuestionResponse.objects.filter(
            form__status='submitted',
            question=time_question
        ).values('response_text').annotate(count=Count('response_text'))
        for item in time_data:
            time_responses[item['response_text']] = item['count']

    if employee_question:
        employee_data = QuestionResponse.objects.filter(
            form__status='submitted',
            question=employee_question
        ).values('response_text').annotate(count=Count('response_text'))
        for item in employee_data:
            employee_responses[item['response_text']] = item['count']

    if error_question:
        error_data = QuestionResponse.objects.filter(
            form__status='submitted',
            question=error_question
        ).values('response_text').annotate(count=Count('response_text'))
        for item in error_data:
            error_responses[item['response_text']] = item['count']

    # Prepare chart data for responses
    time_labels = list(time_responses.keys()) or ['High', 'Medium', 'Low']
    time_data = [time_responses[label] for label in time_labels]

    employee_labels = list(employee_responses.keys()) or ['Yes', 'No']
    employee_data = [employee_responses[label] for label in employee_labels]

    error_labels = list(error_responses.keys()) or ['High', 'Medium', 'Low']
    error_data = [error_responses[label] for label in error_labels]

    context = {
        'chart_data': {
            'process_labels': process_labels,
            'process_counts': process_counts,
            'time_labels': time_labels,
            'time_data': time_data,
            'employee_labels': employee_labels,
            'employee_data': employee_data,
            'error_labels': error_labels,
            'error_data': error_data,
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