from django.urls import path
from django.contrib import admin
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .models import  LoginForm, api, MaaS, connect, disconnect
import sys
from django.urls import include, re_path
from django.shortcuts import redirect



urlpatterns = [
path('machines/', views.machines, name='machines'), #liste des machines
path('machines/<str:maas_id>/', views.show_maas, name='show_maas'), #liste des machines d'un maas
path('machines/<str:maas_id>/<str:machine_id>/', views.machine, name='machine'), #détail d'une machine
path('', lambda request: redirect('machines/', permanent=True)),
path('logout/', views.client_logout, name='client_logout'), #logout
path('machines/<str:maas_id>/power/<str:machine_id>/<str:state>/', views.change_power_state, name='change_power_state'), #changer l'état d'une machine
path('login/local/', views.locallogin, name='local_login'), #login local
path('machines/<str:maas_id>/alocate/<str:machine_id>/', views.alocatmachinetouser, name='alocate'), #alocation d'une machine a un utilisateur
path('machines/<str:maas_id>/dealocate/<str:machine_id>/', views.releasefromuser, name='dealocate'), #dealocation d'une machine a un utilisateur
path('machines/<str:maas_id>/deployform/<str:machine_id>/advanced/', views.deployform_advanced, name='deployform_advanced'), #formulaire de déploiement
path('machines/<str:maas_id>/releaseform/<str:machine_id>/', views.releaseform, name='releaseform'), #formulaire de release
path('machines/<str:maas_id>/release/<str:machine_id>/', views.release, name='release'), #release
path('mkpasswd/', views.mkpasswd, name='mkpasswd'), #génération de mot de passe
path('machines/<str:maas_id>/deploy/<str:machine_id>/advanced/', views.deploy_advanced, name='deployform-advanced'), #déploiement
path('machines/<str:maas_id>/deploy/<str:machine_id>/', views.deploy, name='deploy'), #déploiement
path('machines/<str:maas_id>/deployform/<str:machine_id>/', views.deployform, name='deployform'), #formulaire de déploiement
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = views.handler404 #ajout de la page 404

# run at startup
#object = MaaS.objects.all() # Get all the MaaS objects
#for i in object: # Loop through all the MaaS objects
#    i.connect() # Connect to the MaaS API
#    print("connected", file=sys.stderr) # Print connecte