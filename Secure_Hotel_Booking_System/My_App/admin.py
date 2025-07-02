from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,RoomType,Room,Booking,Payment,AuditLog,SystemConfiguration
############################################################################################################################################################
# In admin.py
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'user_type', 'is_admin', 'is_active', 'created_at')
    list_filter = ('is_admin', 'is_active', 'user_type')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'tc', 'phone_number', 'address')}),
        ('Permissions', {
            'fields': ('user_type', 'is_active', 'is_admin', 'is_staff', 'groups', 'user_permissions'),
        }),
        ('Security info', {
            'fields': ('failed_login_attempts', 'account_locked'),  # Removed last_password_change
        }),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'tc', 'user_type', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('last_password_change', 'created_at', 'updated_at')  # Add readonly fields
    
    search_fields = ('email', 'name')
    ordering = ('-created_at',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        
        if not is_superuser:
            form.base_fields['is_admin'].disabled = True
            form.base_fields['user_permissions'].disabled = True
            form.base_fields['groups'].disabled = True
            
        return form
###################################################################################################################################################################
admin.site.register(User,CustomUserAdmin)
admin.site.register(Room)
admin.site.register(RoomType)
admin.site.register(Payment)
admin.site.register(Booking)
admin.site.register(AuditLog)
admin.site.register(SystemConfiguration)
######################################################################################################################################################################
#Now register the new UserAdmin...
admin.site.site_header="Secure_Hotel_Booking_Management_System|Admin Panel"
admin.site.site_title="Admin Panel"