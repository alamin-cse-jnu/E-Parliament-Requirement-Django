from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # Authentication routes
    #path('login/', LoginView.as_view(template_name='requirements_app/login.html'), name='login'),
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User routes
    path('', views.dashboard, name='dashboard'),
    path('form/', views.form_view, name='form'),
    path('form/<int:form_id>/', views.form_view, name='form_view'),
    path('view-form/', views.view_form, name='view_form'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
    path('view-submissions/', views.view_submissions, name='view_submissions'),
    path('view-form/<int:form_id>/', views.view_form, name='view_form'),
    path('download-pdf/<int:form_id>/', views.download_pdf, name='download_pdf'),
    path('delete-draft/<int:form_id>/', views.delete_draft, name='delete_draft'),
    path('review-form/', views.review_form, name='review_form'),
    path('edit-form/', views.edit_form, name='edit_form'),
    path('confirm-submission/', views.confirm_submission, name='confirm_submission'),
    path('download-review-pdf/', views.download_review_pdf, name='download_review_pdf'),
    # Admin routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('register-user/', views.register_user, name='register_user'),
    path('reset-password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('change-role/<int:user_id>/', views.change_role, name='change_role'),
    path('view-responses/', views.view_responses, name='view_responses'),
    path('view-user-form/<int:form_id>/', views.view_user_form, name='view_user_form'),
    path('delete-form/<int:form_id>/', views.delete_form, name='delete_form'),
    path('data-analysis/', views.data_analysis, name='data_analysis'),
    path('download-user-list/', views.download_user_list, name='download_user_list'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('download-user-pdf/<int:form_id>/', views.download_user_pdf, name='download_user_pdf'),
    path('reports/', views.reports, name='reports'),
    
    # Form structure management routes(Admin)
    path('manage-form-structure/', views.manage_form_structure, name='manage_form_structure'),
    path('add-section/', views.edit_section, name='add_section'),
    path('edit-section/<int:section_id>/', views.edit_section, name='edit_section'),
    path('delete-section/<int:section_id>/', views.delete_section, name='delete_section'),
    path('add-question/<int:section_id>/', views.edit_question, name='add_question'),
    path('edit-question/<int:section_id>/<int:question_id>/', views.edit_question, name='edit_question'),
    path('delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('delete-attachment/<int:form_id>/', views.delete_attachment, name='delete_attachment'),
    path('edit-submitted-form/<int:form_id>/', views.edit_submitted_form, name='edit_submitted_form'),

    # Reports routes
    path('reports/', views.reports, name='reports'),
    path('download-excel-report/', views.download_excel_report, name='download_excel_report'),
]