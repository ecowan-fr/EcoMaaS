# Ecowan-MAAS
A client Interface for MaaS

## Features
- Login via OpenID Connect
- Assign Machine to user
- Deploy Machine from Client
- CloudInit Templates
- User Can Deploy Machines and Release (Configurable)
- Support Multiple MaaS Instances


## Build
```
docker build -t ecomaas .
```

## ENV file 
```
OIDC_RP_CLIENT_ID = ""
OIDC_RP_CLIENT_SECRET = ""
OIDC_OP_AUTHORIZATION_ENDPOINT = ""
OIDC_OP_TOKEN_ENDPOINT = ""
OIDC_OP_USER_ENDPOINT = ""
OIDC_RP_SIGN_ALGO="RS256"
OIDC_OP_JWKS_ENDPOINT=""
DJANGO_ALLOWED_HOSTS=*
DEBUG=1
SECRET_KEY=foo
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=ecomaas
SQL_USER=ecomaas
SQL_PASSWORD=ecomaas
SQL_HOST=db
SQL_PORT=5432
```

For WHCMS
```
OIDC_RP_CLIENT_ID = "CLIENTID"
OIDC_RP_CLIENT_SECRET = "CLIENT SECRET"
OIDC_OP_AUTHORIZATION_ENDPOINT = "https://HOST/oauth/authorize.php"
OIDC_OP_TOKEN_ENDPOINT = "https://HOST/oauth/token.php"
OIDC_OP_USER_ENDPOINT = "https://HOST/oauth/userinfo.php?access_token="
OIDC_RP_SIGN_ALGO="RS256"
OIDC_OP_JWKS_ENDPOINT="https://HOST/oauth/certs.php"
```

## RUN 
Don't forget to create the .env.dev file first

```
cd EcoMaaS/EcOMaaS/
docker-compose up -d --build
docker-compose exec web python manage.py migrate --noinput

```
# Admin Side
## Cloud init 
CLient can deploy a Machine and Define a Password, it will use the stored Cloud-Init by the admin and it will replace $PSSWD with the password and $PHASH with the hashed password
