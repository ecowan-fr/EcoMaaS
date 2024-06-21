from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Server, MaaS, CloudInit, OS
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


class ServerInline(admin.StackedInline):
    model = Server
    can_delete = True
    verbose_name_plural = "Servers"



# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [ServerInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(MaaS)
admin.site.register(CloudInit)
admin.site.register(OS)
