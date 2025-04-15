from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None
            
        # Admin paths
        admin_paths = [
            '/admin-dashboard/',
            '/user-management/',
            '/register-user/',
            '/reset-password/',
            '/change-role/',
            '/view-responses/',
            '/view-user-form/',
            '/delete-form/',
            '/data-analysis/',
            '/download-user-list/',
        ]
        
        # Check if the path is an admin path
        is_admin_path = any(request.path.startswith(path) for path in admin_paths)
        
        # If user is not an admin but trying to access admin path
        if is_admin_path and request.user.role != 'admin':
            messages.error(request, "You don't have permission to access this resource.")
            return redirect('dashboard')
            
        return None