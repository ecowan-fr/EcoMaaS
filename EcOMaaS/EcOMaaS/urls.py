"""
URL configuration for EcOMaaS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.urls import re_path

admin.site.site_header = 'EcoMaaS'                    # default: "Django Administration"
admin.site.index_title = 'EcoMaaS'                 # default: "Site administration"
admin.site.site_title = 'EcoMaaS' #



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('clients/', include('Clients.urls')),
    path('', lambda request: redirect('clients/', permanent=True)),
    path('oidc/', include('mozilla_django_oidc.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

