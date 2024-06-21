import json
from datetime import datetime
from django.conf import settings

import hashlib
import hmac
from .models import Mail, MailEvent
from django.http import HttpResponse
from django.views import View
from django.utils.crypto import constant_time_compare
from django.utils.timezone import utc
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class WebhookView(View):
    def _handle_mailgun_v3(self, request, *args, **kwargs):
        events = {
            'clicked': MailEvent.CLICKED,
            'opened': MailEvent.OPENED,
        }

        try:
            token = request.POST['token']
            timestamp = int(request.POST['timestamp'])
            signature = str(request.POST['signature'])
            event = request.POST['event']
            recipient = request.POST['recipient']

        except KeyError:
            return HttpResponse(status=400)

        expected_signature = hmac.new(key=bytes(settings.MAAS['API_KEY'], 'ascii'), msg=bytes('{}{}'.format(timestamp, token), 'ascii'), digestmod=hashlib.sha256).hexdigest()

        if not constant_time_compare(signature, expected_signature):
            return HttpResponse(status=400)

        try:
            args = {
                'type': events[event],
                'recipient': recipient,
                'timestamp': datetime.fromtimestamp(timestamp),
                'url': request.POST.get('url', '')
            }
            event = MailEvent.objects.create(**args) 

        except:
            pass

        return HttpResponse(status=200)

    @method_decorator(csrf_exempt)
    def post(self, *args, **kwargs):
        provider_methods = {
            'MAILGUN_V3': self._handle_mailgun_v3
        }

        if 'PROVIDER' not in settings.MAAS:
            raise MaasConfigurationException('MAAS.PROVIDER must be set')

        if settings.MAAS['PROVIDER'] not in provider_methods:
            raise MaasConfigurationException('MAAS.PROVIDER is invalid')

        return provider_methods[settings.MAAS['PROVIDER']](*args, **kwargs)
