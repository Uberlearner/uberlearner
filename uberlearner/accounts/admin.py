from django.contrib import admin
from accounts.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'dob', 'summary'),
        }),
    )

admin.site.register(UserProfile, UserProfileAdmin)
