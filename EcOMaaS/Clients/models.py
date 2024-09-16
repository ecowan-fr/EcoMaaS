from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms
from django.contrib import admin
from oauthlib.oauth1 import SIGNATURE_PLAINTEXT
from requests_oauthlib import OAuth1Session
import sys
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import base64
# Create your models here.

from django.contrib.auth.models import User

api = [] # list of all the maas api's

class Server(models.Model): # Server model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    servers = models.TextField(blank=False,default="[]")


class LoginForm(forms.Form): # Login form
    username = forms.CharField(max_length=63)
    password = forms.CharField(max_length=63, widget=forms.PasswordInput)

class MaaS(models.Model): # MaaS model for storing the MaaS credentials 
    MAAS_HOST = models.CharField(max_length=255) # MaaS host
    # CONSUMER_KEY, CONSUMER_TOKEN, SECRET = "<API-KEY>".split(":")
    CONSUMER_KEY = models.CharField(max_length=255) # MaaS consumer key
    CONSUMER_TOKEN = models.CharField(max_length=255) # MaaS consumer token
    SECRET = models.CharField(max_length=255) # MaaS secret
    Name = models.CharField(max_length=255)         # MaaS name
    editable = models.BooleanField(default=True)   # MaaS editable by user  
    
    class Meta: # Meta class, how is the model displayed in the admin panel
        verbose_name = 'MaaS' 
        verbose_name_plural = 'MaaS'
    def __str__(self):
        return self.Name
    
    def connect(self): # Connect to the MaaS API
        for i in api:
            if i['name'] == self.Name:
                print("already connected", file=sys.stderr)
                pass
            else:
                api.append({'url': f"{self.MAAS_HOST}/MAAS/api/2.0/", 'name': self.Name, "api": OAuth1Session(self.CONSUMER_KEY, resource_owner_key=self.CONSUMER_TOKEN, resource_owner_secret=self.SECRET, signature_method=SIGNATURE_PLAINTEXT)}) # Append the API to the list of all the API's
                print(api, file=sys.stderr)
        return api
    def disconnect(self): # Disconnect from the MaaS API
        for i in api: # Loop through all the API's
            if i['name'] == self.Name: # If the name of the API is the same as the name of the MaaS object
                api.remove(i) # Remove the API from the list of all the API's
        print(api, file=sys.stderr) # Print the list of all the API's
        return api

@receiver(post_save, sender=MaaS) # When a MaaS object is saved
def connect(sender, instance, **kwargs): # Connect to the MaaS API
    instance.connect() # Connect to the MaaS API
    print("connected", file=sys.stderr)  # Print connected
    return api
 
@receiver(post_delete, sender=MaaS) # When a MaaS object is deleted
def disconnect(sender, instance, **kwargs): 
    instance.disconnect() # Disconnect from the MaaS API 
    print("disconnected", file=sys.stderr)
    return api


class CloudInit(models.Model): # Cloud-Init model
    name = models.CharField(max_length=255, default="cloud-init") # Name of the cloud-init
    os = models.CharField(default="ubuntu", max_length=8000,blank=True) # OS of the cloud-init
    userdata = models.TextField(default="#cloud-config", max_length=8000,blank=True) # Userdata of the cloud-init
    class meta: # Meta class, how is the model displayed in the admin panel
        verbose_name = 'Cloud-Init' 
        verbose_name_plural = 'Cloud-Inits'
    def __str__(self): # String representation of the object
        return self.name
    
class OS(models.Model): # OS model
    name = models.CharField(max_length=255, default="Debian 12") # Name of the OS
    value = models.CharField(max_length=255 , default="custom/debian-12") # name of the OS in MaaS 
    storage_layout = models.TextField(max_length=255, default="flat") # Storage layout of the OS
    def __str__(self): # String representation of the object
        return self.name
    class Meta: # Meta class, how is the model displayed in the admin panel
        verbose_name = 'OS'
        verbose_name_plural = 'OS'
    


