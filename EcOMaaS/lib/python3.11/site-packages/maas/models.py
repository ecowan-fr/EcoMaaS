from django.db import models
from django.conf import settings
from django.template import loader
from .exceptions import *
import requests

MAILGUN_V3_BASE = 'https://api.mailgun.net/v3'

MAIL_STATUSES = [
    (0, '')
]


class MailManager(models.Manager):
    def create_from_template(self, **kwargs):
        """
        Creates a Mail record with a body loaded from a Django template
        """
        try:
            template_name = kwargs.pop('template')
        except:
            raise MaasException('create_from_template requires the `template` kwarg')

        template = loader.get_template(template_name)
        context = kwargs.pop('context', {})

        if not hasattr(settings, 'MAAS'):
            raise MaasConfigurationException('MAAS must be defined in settings')

        if 'OPTIONS' in settings.MAAS and 'context_processors' in settings.MAAS['OPTIONS']:
            for context_processor_ref in settings.MAAS['OPTIONS']['context_processors']:
                split = context_processor_ref.split('.')

                module = __import__('.'.join(split[0:-1]))
                for s in split[1:]:
                    module = getattr(module, s)

                context.update(module())

        rendered = template.render(context)
        kwargs['body'] = rendered
        return self.create(**kwargs)


class Mail(models.Model):
    sender = models.EmailField()
    sender_title = models.CharField(blank=True, null=True, default='', max_length=200)
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField(max_length=5000)
    delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MailManager()

    class Meta:
        verbose_name_plural = 'Mail'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(settings, 'MAAS'):
            raise MaasConfigurationException('MAAS must be defined in settings')

        if not self.sender and 'DEFAULT_SENDER' in settings.MAAS:
            self.sender = settings.MAAS['DEFAULT_SENDER']

        if not self.sender_title and 'DEFAULT_SENDER_TITLE' in settings.MAAS:
            self.sender_title = settings.MAAS['DEFAULT_SENDER_TITLE']

    def _send_mailgun_v3(self):
        if 'DOMAIN' not in settings.MAAS:
            raise MaasConfigurationException('MAAS.DOMAIN must be defined in settings')

        if 'API_KEY' not in settings.MAAS:
            raise MaasConfigurationException('MAAS.DOMAIN must be defined in settings')

        url = '{}/{}/messages'.format(MAILGUN_V3_BASE, settings.MAAS['DOMAIN'])
        auth = ('api', settings.MAAS['API_KEY'])
        data = {
            'from': '{} <{}>'.format(self.sender_title, self.sender),
            'to': [ self.recipient ],
            'subject': self.subject,
            'html': self.body
        }

        res = requests.post(url, auth=auth, data=data)

        if res.status_code == 400:
            raise MaasUnknownException('Mailgun reported a bad request was made. Request body: {}'.format(res.text))

        if res.status_code == 401:
            raise MaasConfigurationException('MAAS.API_KEY seems to be invalid.')

        if res.status_code == 402:
            raise MaasUnknownException('Mailgun reported that the parameters were valid but the request failed. It is unclear what this means. Please report this error to django-maas.')

        if res.status_code == 404:
            raise MaasConfigurationException('MAAS.DOMAIN seems to be invalid,')

        if res.status_code in [500, 502, 503, 504]:
            raise MaasProviderException('Mailgun encountered an error on their end')

        try:
            res.raise_for_status()
        except:
            raise MaasUnknownException('Mailgun returned an undocumented status code {}. Please report this error to django-maas.'.format(res.status_code))

        self.delivered = True
        self.save()

    def send(self):
        provider_methods = {
            'MAILGUN_V3': self._send_mailgun_v3
        }

        if 'PROVIDER' not in settings.MAAS:
            raise MaasConfigurationException('MAAS.PROVIDER must be set')

        if settings.MAAS['PROVIDER'] not in provider_methods:
            raise MaasConfigurationException('MAAS.PROVIDER is invalid')

        provider_methods[settings.MAAS['PROVIDER']]()


class MailEvent(models.Model):
    CLICKED = 6
    OPENED = 7

    TYPE_CHOICES = [
        (CLICKED, 'CLICKED'),
        (OPENED, 'OPENED'),
    ]

    type = models.IntegerField(choices=TYPE_CHOICES)
    recipient = models.CharField(max_length=200)
    timestamp = models.DateTimeField()
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.recipient