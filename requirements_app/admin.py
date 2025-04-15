from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, RequirementForm, FormSection, FormQuestion, QuestionResponse

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'user_id', 'get_full_name', 'designation', 'wing_name', 'department_name', 'section_name', 'mobile', 'role')
    list_filter = ('role', 'wing_name', 'department_name')
    search_fields = ('username', 'first_name', 'last_name', 'user_id')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'designation', 'wing_name', 'department_name', 'section_name', 'mobile', 'photo', 'signature')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'designation', 'wing_name', 'department_name', 'section_name', 'mobile', 'photo', 'signature', 'role'),
        }),
    )
    actions = ['reset_password']

    def user_id(self, obj):
        return obj.username  # Since the model doesn't have a separate user_id field, using username as user_id
    user_id.short_description = 'User ID'

    def reset_password(self, request, queryset):
        for user in queryset:
            user.set_password('newpassword123')  # Customize this
            user.save()
        self.message_user(request, "Passwords reset successfully.")
    reset_password.short_description = "Reset selected users' passwords"

@admin.register(RequirementForm)
class RequirementFormAdmin(admin.ModelAdmin):
    list_display = ('process_name', 'user', 'status', 'created_at', 'submitted_at')
    list_filter = ('status', 'created_at', 'submitted_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'process_name')
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        queryset.delete()
    delete_selected.short_description = "Delete selected responses"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
@admin.register(FormSection)
class FormSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('order',)
    actions = ['activate_sections', 'deactivate_sections']

    def activate_sections(self, request, queryset):
        queryset.update(is_active=True)
    activate_sections.short_description = "Activate selected sections"

    def deactivate_sections(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_sections.short_description = "Deactivate selected sections"

class QuestionInline(admin.TabularInline):
    model = FormQuestion
    extra = 1
    fields = ('question_text', 'field_type', 'options', 'is_required', 'order', 'is_active')

@admin.register(FormQuestion)
class FormQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'section', 'field_type', 'is_required', 'order', 'is_active')
    list_filter = ('section', 'field_type', 'is_required', 'is_active')
    search_fields = ('question_text', 'section__title')
    ordering = ('section', 'order')

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('form', 'question', 'truncated_response')
    list_filter = ('question__section', 'form__status')
    search_fields = ('form__user__username', 'question__question_text', 'response_text')
    
    def truncated_response(self, obj):
        if len(obj.response_text) > 50:
            return obj.response_text[:50] + "..."
        return obj.response_text
    truncated_response.short_description = "Response"