from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer

class AccountAdmin(UserAdmin):
    list_display = ('email', 'date_joined', 'last_login', 'is_admin', 'is_staff',)
    search_fields = ('email',)
    readonly_fields = ('date_joined', 'last_login',)
    ordering = ('email',)


    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(User, AccountAdmin)
admin.site.register(Customer)