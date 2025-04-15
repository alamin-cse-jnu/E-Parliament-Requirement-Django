# utils.py

from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from django.conf import settings
import tempfile
import os
from datetime import datetime
import base64
from django.templatetags.static import static
from django.contrib.staticfiles import finders

def get_static_file_as_data_uri(path):
    """Convert a static file to a data URI for embedding in HTML"""
    # First try to find the absolute path
    abs_path = finders.find(path)
    
    if not abs_path:
        # Try a direct path
        if os.path.exists(path):
            abs_path = path
        else:
            # Try with STATIC_ROOT
            full_path = os.path.join(settings.STATIC_ROOT, path)
            if os.path.exists(full_path):
                abs_path = full_path
            else:
                # One more attempt with BASE_DIR
                full_path = os.path.join(settings.BASE_DIR, 'requirements_app', 'static', path)
                if os.path.exists(full_path):
                    abs_path = full_path
                else:
                    print(f"Warning: Could not find static file: {path}")
                    return None
    
    # Read the file and encode it
    try:
        with open(abs_path, 'rb') as f:
            file_content = f.read()
        
        # Get mime type based on file extension
        _, ext = os.path.splitext(abs_path)
        mime_type = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        }.get(ext.lower(), 'application/octet-stream')
        
        # Create data URI
        data_uri = f"data:{mime_type};base64,{base64.b64encode(file_content).decode('utf-8')}"
        return data_uri
    except Exception as e:
        print(f"Error processing static file {path}: {str(e)}")
        return None

def generate_pdf(form):
    # Get user from form
    user = form.user
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Set current date
    current_date = datetime.now()
    
    # Get signature data if available
    signature_data_uri = None
    if user.signature:
        try:
            with open(user.signature.path, 'rb') as f:
                signature_content = f.read()
                _, ext = os.path.splitext(user.signature.path)
                mime_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif'
                }.get(ext.lower(), 'image/jpeg')
                signature_data_uri = f"data:{mime_type};base64,{base64.b64encode(signature_content).decode('utf-8')}"
        except Exception as e:
            print(f"Error processing signature: {str(e)}")

    # Fetch all sections with questions and answers
    from .models import FormSection, QuestionResponse
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
    
    # Render HTML content
    html_string = render_to_string('requirements_app/pdf/form_template.html', {
        'form': form,
        'user': user,
        'logo_data_uri': logo_data_uri,
        'signature_data_uri': signature_data_uri,
        'current_date': current_date,
        'sections_with_answers': sections_with_answers
    })
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output:
        # Generate PDF
        HTML(string=html_string).write_pdf(
            output,
            stylesheets=[
                CSS(string='@page { size: A4; margin: 1.5cm }')
            ]
        )
        output_path = output.name
    
    # Read the generated PDF
    with open(output_path, 'rb') as f:
        pdf_content = f.read()
    
    # Clean up the temporary file
    os.unlink(output_path)
    
    return pdf_content

def generate_user_list_pdf():
    from .models import User
    users = User.objects.all().order_by('role', 'username')
    
    # Get logo as data URI
    logo_data_uri = get_static_file_as_data_uri('images/parliament_logo.png')
    
    # Current date
    current_date = datetime.now()
    
    # Render HTML content
    html_string = render_to_string('requirements_app/pdf/user_list_template.html', {
        'users': users,
        'logo_data_uri': logo_data_uri,
        'current_date': current_date
    })
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output:
        # Generate PDF
        HTML(string=html_string).write_pdf(
            output,
            stylesheets=[
                CSS(string='@page { size: A4 landscape; margin: 1cm }')
            ]
        )
        output_path = output.name
    
    # Read the generated PDF
    with open(output_path, 'rb') as f:
        pdf_content = f.read()
    
    # Clean up the temporary file
    os.unlink(output_path)
    
    return pdf_content

# Add these functions to utils.py

def generate_report_pdf(template_name, context_data, filename="report.pdf"):
    """Generic function to generate PDF from a template"""
    html_string = render_to_string(template_name, context_data)
    
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