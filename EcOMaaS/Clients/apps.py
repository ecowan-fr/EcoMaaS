from django.apps import AppConfig
from .models import  LoginForm, api, MaaS, connect, disconnect
import sys




class ClientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Clients'
    def ready(self):
        object = MaaS.objects.all() # Get all the MaaS objects
        for i in object: # Loop through all the MaaS objects
            i.connect() # Connect to the MaaS API
            print("connected", file=sys.stderr) # Print connected

# run at startup
