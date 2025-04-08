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
    
    # Render HTML content
    html_string = render_to_string('requirements_app/pdf/form_template.html', {
        'form': form,
        'user': user,
        'logo_data_uri': logo_data_uri,
        'current_date': current_date
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