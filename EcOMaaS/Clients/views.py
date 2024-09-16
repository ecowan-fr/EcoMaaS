from django.shortcuts import render
import sys # Import the sys module
from requests_oauthlib import OAuth1Session # Import the OAuth1Session class from the requests_oauthlib module
import json  # Import the json module
from django.contrib.auth.decorators import login_required # Import the login_required decorator
from django.shortcuts import redirect # Import the redirect function
from django.template import RequestContext # Import the RequestContext class
from django.contrib.auth import authenticate, login, logout # Import the authenticate and login functions
from .models import  LoginForm, api, MaaS, OS, CloudInit # Import the LoginForm, api, MaaS, OS, and CloudInit models
from django.contrib.admin.views.decorators import staff_member_required # Import the staff_member_required decorator
from hashlib import sha256 # Import the sha256 function from the hashlib module for generating the password hash
import base64
import crypt
import os
import string 
from random import SystemRandom # Import the SystemRandom class
    
Debug = True # Set the Debug variable to False

# Create your views here.
@login_required(login_url='/accounts/login/') #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def machines(request): #fonction qui permet d'afficher les machines
    connect_maasapi() #connecte les api
    machine = {} 
    print(maasapi, file=sys.stdout)
    for maasapi in api:
        response = maasapi["api"].get(f"{maasapi['url']}machines/") #récupère les machines
        machine[maasapi['name']] = json.loads(response.content) #stocke les machines dans un dictionnaire
        print(response.content, file=sys.stdout)
    return render(request, 'machines.html', {'dic_machines': machine})

@login_required(login_url='/accounts/login/')
def show_maas(request,maas_id): #fonction qui permet d'afficher les machines d'un maas
    connect_maasapi() #connecte les api
    machine_maas = {}
    for maasapi in api: #parcours les api
        if maasapi['name'] == maas_id: #si le nom de l'api est égal à l'id du maas
            response = maasapi["api"].get(f"{maasapi['url']}machines/")     #récupère les machines
            machine_maas[maasapi['name']] = json.loads(response.content)
            if Debug:
                print(response.content, file=sys.stderr)
            return render(request, 'machines.html', {'dic_machines': machine_maas, 'maas_id': maas_id}) #affiche les machines
    return  render(request,'404.html', {}) #affiche une erreur 404 si le maas n'existe pas




@login_required(login_url='/accounts/login/') #si l'utilisateur n'est pas connecté, il est redirigé vers la page de connexion
def machine(request, machine_id, maas_id): #fonction qui permet d'afficher une machine
    connect_maasapi() #connecte les api
    for maasapi in api:
        if maasapi['name'] == maas_id:
            edit_by_user = MaaS.objects.get(Name=maas_id).editable #récupère les informations de l'api
            response = maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/") #récupère les informations de la machine
            machine = json.loads(response.content)
            return render(request, 'machine.html', {'machine': machine, 'maas_id': maas_id, 'edit_by_user': edit_by_user})
    return  render(request,'404.html', {})



def client_logout(request): #fonction qui permet de se déconnecter
    logout(request) #déconnecte l'utilisateur
    return redirect('/clients/') #redirige vers la page d'accueil
 
@login_required(login_url='/accounts/login/')
def change_power_state(request, machine_id, state, maas_id): #fonction qui permet de changer l'état de la machine
    connect_maasapi() #connecte les api
    for maasapi in api:
        if maasapi['name'] == maas_id:
            if state == "on": #si l'état est "on"
                if request.user.email == json.loads(maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/").content)['description'] or request.user.is_superuser: #si l'utilisateur est le propriétaire de la machine ou s'il est super utilisateur
                    if Debug:
                        print("User change power state Mahcine %s on"%(machine_id), file=sys.stderr) #affiche un message
                    response = maasapi["api"].post(f"{maasapi['url']}machines/{machine_id}/op-power_on") #allume la machine
                else:
                    print("error auth on", file=sys.stderr) #affiche une erreur
            elif state == "off": #si l'état est "off"
                if request.user.username == json.loads(maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/").content)['owner'] or request.user.is_superuser:
                    if Debug:
                        print("User change power state Mahcine %s off"%(machine_id), file=sys.stderr)
                    response = maasapi["api"].post(f"{maasapi['url']}machines/{machine_id}/op-power_off")
                else:
                    print("error auth off", file=sys.stderr) #affiche une erreur
            return redirect('/clients/machines/'  + maas_id + '/' + machine_id + '/') #redirige vers la page de la machine


def handler404(request, *args, **argv): ##prend en compte le ereurs 404
    response = render('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response

def locallogin(request): #fonction qui permet de se connecter en local
    if request.method == 'POST': #si la méthode est POST
        form = LoginForm(request.POST) #récupère les informations du formulaire
        if form.is_valid(): #si le formulaire est valide
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password) #authentifie l'utilisateur
            if user: #si l'utilisateur est authentifié
                login(request, user)     #connecte l'utilisateur
                return redirect('machines') #redirige vers la page des machines
        else:
            form = LoginForm() #sinon, réaffiche le formulaire
            return render(request, 'localogin.html', {'form': form}) #affiche le formulaire
    form = LoginForm()
    return render(request, 'localogin.html', {'form': form})

@staff_member_required #seul le staff peut accéder à cette page
def alocatmachinetouser(request, machine_id, maas_id): #fonction qui permet d'attribuer une machine à un utilisateur
    connect_maasapi() #connecte les api
    if request.user.is_superuser: #si l'utilisateur est super utilisateur
        if request.method == 'POST': #si la méthode est POST
            email = request.POST.get('email') #récupère l'email
            for maasapi in api: #parcours les api
                if maasapi['name'] == maas_id:
                    response =  maasapi["api"].put(f"{maasapi['url']}machines/{machine_id}/", data={'description': str(email)}) #attribue la machine à l'utilisateur 
                    return redirect('/clients/machines/' + maas_id + '/' + machine_id + '/')  #redirige vers la page de la machine
        else:
            return  render(request,'404.html', {}) #affiche une erreur 404
    else:
        return  render('404.html', {}) #affiche une erreur 404
    
@staff_member_required
def releasefromuser(request, machine_id, maas_id): #fonction qui permet de libérer une machine
    connect_maasapi() #connecte les api
    if request.user.is_superuser: #si l'utilisateur est super utilisateur
        if request.method == 'POST':
            for maasapi in api:
                if maasapi['name'] == maas_id:
                    response =  maasapi["api"].put(f"{maasapi['url']}machines/{machine_id}/", data={'description': ''}) #libère la machine
                    return redirect('/clients/machines/' + maas_id + '/' + machine_id + '/') #redirige vers la page de la machine
            return  render(request,'404.html', {})
        else:
            return  render(request,'404.html', {})
    else:  
        return  render(request,'404.html', {})

@login_required(login_url='/accounts/login/')
def deployform_advanced(request, machine_id, maas_id): #fonction qui permet de déployer une machine
    connect_maasapi() #connecte les api
    oslist = OS.objects.all().order_by('name') #récupère la liste des OS
    CloudInitList = CloudInit.objects.all().order_by('name') #récupère la liste des CloudInit
    for maasapi in api:
        if maasapi['name'] == maas_id:
            response = maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/") #récupère les informations de la machine
            machine = json.loads(response.content) #stocke les informations de la machine

    return render(request, 'deployform-advandced.html', {'maas_id': maas_id, 'machine_id': machine_id, 'machine': machine, 'oslist': oslist, 'CloudInitList': CloudInitList}) #affiche le formulaire de déploiement

@login_required(login_url='/accounts/login/')
def deployform(request, machine_id, maas_id): #fonction qui permet de déployer une machine
    connect_maasapi() #connecte les api
    oslist = OS.objects.all().order_by('name') #récupère la liste des OS
    CloudInitList = CloudInit.objects.all().order_by('name') #récupère la liste des CloudInit
    for maasapi in api:
        if maasapi['name'] == maas_id:
            response = maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/") #récupère les informations de la machine
            machine = json.loads(response.content) #stocke les informations de la machine

    return render(request, 'deployform.html', {'maas_id': maas_id, 'machine_id': machine_id, 'machine': machine, 'oslist': oslist, 'CloudInitList': CloudInitList}) #affiche le formulaire de déploiement



@login_required(login_url='/accounts/login/')
def releaseform(request, machine_id, maas_id): #fonction qui permet d'afficher le formulaire de libération
    connect_maasapi() #connecte les api
    for maasapi in api: #parcours les api
        if maasapi['name'] == maas_id:
            response = maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/") #récupère les informations de la machine
            machine = json.loads(response.content)
    return render(request, 'releaseform.html', {machine_id: machine_id, 'maas_id': maas_id, 'machine': machine}) #affiche le formulaire de libération

@login_required(login_url='/accounts/login/')
def release(request, machine_id, maas_id): #fonction qui permet de libérer une machine
    connect_maasapi() #connecte les api
    if request.method == 'POST':
        quick_erase = request.POST.get('quick_erase') #récupère les informations du formulaire
        secure_erase = request.POST.get('secure_erase') #récupère les informations du formulaire
        erase = (quick_erase or secure_erase) # si quick_erase ou secure_erase est vrai, les données sont effacées
        for maasapi in api:
            if maasapi['name'] == maas_id:
                if request.user.is_superuser or request.user.email == json.loads(maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/").content)['description']: #si l'utilisateur est super utilisateur ou le propriétaire de la machine
                    response = maasapi["api"].post(f"{maasapi['url']}machines/{machine_id}/op-release", data={'erase': erase, 'quick_erase': quick_erase, 'secure_erase': secure_erase}) #libère la machine
                    return redirect('/clients/machines/' + maas_id + '/' + machine_id + '/') #redirige vers la page de la machine
                else:
                    return  render(request,'404.html')
            
    else:
        return  render(request,'404.html')

@login_required(login_url='/accounts/login/') 
def mkpasswd(request): #fonction qui permet de générer un mot de passe
  if request.method == 'POST': 
    password = request.POST.get('password') #récupère le mot de passe
    hash = sha512_crypt(password) #génère le mot de passe
    return render(request, 'mkpasswd.html', {'hash': hash}) #affiche le mot de passe
  else:
    return render(request, 'mkpasswd.html', {})  #affiche le formulaire

def connect_maasapi():
    object = MaaS.objects.all() # Get all the MaaS objects
    print(object, file=sys.stdout)
    for i in object: # Loop through all the MaaS objects
        maasapi = i.connect()
        print(i.connect(), file=sys.stdout) # Connect to the MaaS API
        print("connected", file=sys.stdout) # Print connecte
    return maasapi


def sha512_crypt(password, salt=None, rounds=None): #fonction qui permet de générer un mot de passe
    randchoice = SystemRandom().choice #génère un mot de passe aléatoire 
    if salt is None:  # genere un salt
        salt = ''.join([randchoice(string.ascii_letters + string.digits) 
                        for _ in range(8)])
 
    prefix = '$6$' 
    if rounds is not None: 
        rounds = max(1000, min(999999999, rounds or 5000))
        prefix += 'rounds={0}$'.format(rounds)
    return crypt.crypt(password, prefix + salt) #retourne le mot de passe

@login_required(login_url='/accounts/login/')
def deploy_advanced(request, machine_id, maas_id): #fonction qui permet de déployer une machine
    connect_maasapi() #connecte les api
    for maasapi in api: #parcours les api
        if maasapi['name'] == maas_id: #si le nom de l'api est égal à l'id du maas
            if request.user.is_superuser or request.user.email == json.loads(maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/").content)['description']: #si l'utilisateur est super utilisateur ou le propriétaire de la machine
                if request.method == 'POST':
                    distro_series = request.POST.get('oslist') #récupère l'os choisi
                    CloudInitObj = request.POST.get('cloudinit').encode('utf-8') #récupère le cloudinit
                    user_data = base64.b64encode(CloudInitObj) #encode le cloudinit
                    response = maasapi["api"].post(f"{maasapi['url']}machines/{machine_id}/op-deploy", data={'distro_series': distro_series, 'user_data': user_data}) #déploie la machine
                    return redirect('/clients/machines/' + maas_id + '/' + machine_id + '/')
                else:
                    oslist = OS.objects.all().order_by('name') #récupère la liste des OS
                    CloudInitList = CloudInit.objects.all().order_by('name') #récupère la liste des CloudInit
                    response = maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/") #récupère les informations de la machine
                    machine = json.loads(response.content) 
                    return render(request, 'deployform-advandced.html', {'maas_id': maas_id, 'machine_id': machine_id, 'machine': machine, 'oslist': oslist, 'CloudInitList': CloudInitList}) #affiche le formulaire de déploiement
            else:
                return  render(request,'404.html', {}) #affiche une erreur 404
            
@login_required(login_url='/accounts/login/')
def deploy(request, machine_id, maas_id):
    connect_maasapi() #connecte les api
    for maasapi in api: #parcours les api
        if maasapi['name'] == maas_id:
            if request.user.is_superuser or request.user.email == json.loads(maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/").content)['description']:
                if request.method == 'POST':
                    distro_series = request.POST.get('oslist') #récupère l'os choisi
                    password = request.POST.get('password') #récupère le mot de passe
                    hash_password = sha512_crypt(password) #génère le mot de passe
                    distro=distro_series.split("/")[0]
                    CloudInitObj = CloudInit.objects.filter(os=distro) #récupère la liste des CloudInit
                    Cloudinit = CloudInitObj[0].userdata.replace("$PSSWD", password) #remplace le mot de passe dans le cloudinit
                    Cloudinit = Cloudinit.replace("$PHASH", hash_password) #remplace le mot de passe hashé dans le cloudinit
                    user_data = base64.b64encode(Cloudinit.encode('utf-8')) #encode le cloudinit
                    if Debug:
                        print("User deploy Mahcine %s"%(machine_id), file=sys.stderr)
                        print("User deploy Mahcine Cloud Init%s"%(user_data), file=sys.stderr)
                    response = maasapi["api"].post(f"{maasapi['url']}machines/{machine_id}/op-deploy", data={'distro_series': distro_series, 'user_data': user_data})
                    return redirect('/clients/machines/' + maas_id + '/' + machine_id + '/')
                else:
                    oslist = OS.objects.all().order_by('name') #récupère la liste des OS
                    CloudInitList = CloudInit.objects.all().order_by('name') #récupère la liste des CloudInit
                    response = maasapi["api"].get(f"{maasapi['url']}machines/{machine_id}/") #récupère les informations de la machine
                    machine = json.loads(response.content) 
                    return render(request, 'deployform.html', {'maas_id': maas_id, 'machine_id': machine_id, 'machine': machine, 'oslist': oslist, 'CloudInitList': CloudInitList}) #affiche le formulaire de déploiement
            else:
                return  render(request,'404.html', {}) #affiche une erreur 404
