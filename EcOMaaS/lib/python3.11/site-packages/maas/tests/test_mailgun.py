from django.test import TestCase, override_settings, Client
from maas.exceptions import *
from maas.models import *
from datetime import datetime
import responses
import re
import requests


class MailgunV3Test(TestCase):

    def setUp(self):
        def buildMail():
            return Mail(sender='test@test.com', recipient='test@test.com', subject='subject', body='body')

        self.buildMail = buildMail

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3'})
    def test_no_domain(self):
        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test'})
    def test_no_api_key(self):
        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_invalid_api_key(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=401)

        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_invalid_domain(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=404)

        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_mailgun_error(self):
        for status in [500, 502, 503, 504]:
            responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=status)

            with self.assertRaises(MaasProviderException):
                mail = self.buildMail()
                mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_bad_request(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=400)

        with self.assertRaises(MaasUnknownException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_bad_request(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=407)

        with self.assertRaises(MaasUnknownException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_bad_request(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=402)

        with self.assertRaises(MaasUnknownException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DOMAIN': 'test', 'API_KEY': 'test'})
    @responses.activate
    def test_successful_delivery(self):
        responses.add(responses.POST, re.compile(r'^{}/test/messages'.format(MAILGUN_V3_BASE)), status=200)
        mail = self.buildMail()
        mail.save()
        self.assertEqual(mail.delivered, False)
        mail.send()
        mail = Mail.objects.get(id=mail.id)
        self.assertEqual(mail.delivered, True)


class MailgunV3WebhookTest(TestCase):
    def setUp(self):
        WEBHOOK_URI = '/webhook/'
        api = Client()

        def send(data):
            return api.post(WEBHOOK_URI, data=data)

        self.send = send

        def buildMail():
            return Mail(sender='test@test.com', recipient='test@test.com', subject='subject', body='body')

        self.buildMail = buildMail

    def test_invalid_sec(self):
        test_data = {'a': 1}
        res = self.send(test_data)
        self.assertEqual(res.status_code, 400)

    def test_invalid_hmac(self):
        data = {
            'timestamp': 1522339662,
            'token': 'ec37956da8ab6253c165aa26d52641a91345a7673fb3fd3864',
            'signature': 'fake',
            'recipient': 'fake'
        }
        res = self.send(data)
        self.assertEqual(res.status_code, 400)

    def test_valid_hmac(self):
        data = {
            'timestamp': 1522339662,
            'token': 'ec37956da8ab6253c165aa26d52641a91345a7673fb3fd3864',
            'signature': '02473efcee54bf5c3967894718900ff1f877d0af58d6143ab1568fbd3d53afbc',
            'recipient': 'fake',
            'event': 'opened'
        }
        res = self.send(data)
        self.assertEqual(res.status_code, 200)

    def test_mail_found(self):
        mail = self.buildMail()
        mail.api_id = 'fake'
        mail.save()

        data = {
            'timestamp': 1522339662,
            'token': 'ec37956da8ab6253c165aa26d52641a91345a7673fb3fd3864',
            'signature': '02473efcee54bf5c3967894718900ff1f877d0af58d6143ab1568fbd3d53afbc',
            'recipient': 'fake',
            'event': 'clicked'
        }
        res = self.send(data)

        events = MailEvent.objects.filter(recipient='fake')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(events.count(), 1)
        self.assertEqual(events[0].timestamp.replace(tzinfo=None), datetime.fromtimestamp(1522339662))

    def test_url_added(self):
        mail = self.buildMail()
        mail.api_id = 'fake'
        mail.save()

        data = {
            'timestamp': 1522339662,
            'token': 'ec37956da8ab6253c165aa26d52641a91345a7673fb3fd3864',
            'signature': '02473efcee54bf5c3967894718900ff1f877d0af58d6143ab1568fbd3d53afbc',
            'recipient': 'fake',
            'event': 'clicked',
            'url': 'test_url'
        }
        res = self.send(data)

        events = MailEvent.objects.filter(recipient='fake')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(events.count(), 1)
        self.assertEqual(events[0].timestamp.replace(tzinfo=None), datetime.fromtimestamp(1522339662))
        self.assertEqual(events[0].url, 'test_url')