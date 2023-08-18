from django.contrib import admin
from . models import employee

# Register your models here.
admin.site.register(employee)
class employeeadmin():
    list_display = ["id","email", "full_name", "username","is_active","created_at", "is_admin"]
