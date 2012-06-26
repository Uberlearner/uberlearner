from django.contrib import admin
from accounts.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', ('first_name', 'middle_name', 'last_name'), 'dob'),
        }),
    )

admin.site.register(UserProfile, UserProfileAdmin)
