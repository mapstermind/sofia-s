from django.contrib import admin

from .models import LoginToken


@admin.register(LoginToken)
class LoginTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "expires_at", "is_used"]
    list_filter = ["is_used"]
    raw_id_fields = ["user"]
    readonly_fields = ["token", "created_at"]
