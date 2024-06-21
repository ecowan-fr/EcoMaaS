from django.test import TestCase, override_settings
from django.template.exceptions import TemplateDoesNotExist
from maas.exceptions import *
from maas.models import *


class GenericTest(TestCase):

    def setUp(self):

        def buildMail():
            return Mail(sender='test@test.com', recipient='test@test.com', subject='subject', body='body')

        self.buildMail = buildMail

    def test_no_settings(self):
        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={})
    def test_no_provider(self):
        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'UNKNOWN'})
    def test_unknown_provider(self):
        with self.assertRaises(MaasConfigurationException):
            mail = self.buildMail()
            mail.send()

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DEFAULT_SENDER': 'test_sender@wat.com'})
    def test_default_sender(self):
        mail = Mail(recipient='test@test.com', subject='subject', body='body')
        self.assertEqual(mail.sender, 'test_sender@wat.com')

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DEFAULT_SENDER_TITLE': 'test'})
    def test_default_sender_title(self):
        mail = self.buildMail()
        self.assertEqual(mail.sender_title, 'test')

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DEFAULT_SENDER_TITLE': 'test'})
    def test_create_from_template_template_not_provided(self):
        """
        Should fail if user doesn't provide template
        """
        with self.assertRaises(MaasException):
            Mail.objects.create_from_template(recipient='test@test.com', subject='subject')

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DEFAULT_SENDER_TITLE': 'test'})
    def test_create_from_template_template_not_found(self):
        """
        Should fail if user doesn't provide template
        """
        with self.assertRaises(TemplateDoesNotExist):
            Mail.objects.create_from_template(recipient='test@test.com', subject='subject', template='wat')

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DEFAULT_SENDER_TITLE': 'test'})
    def test_create_from_template_success_no_context(self):
        """
        Should render successfully without context
        """
        mail = Mail.objects.create_from_template(recipient='test@test.com', subject='subject', template='test_no_context.html')
        self.assertEqual(mail.body, 'test_no_context')

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DEFAULT_SENDER_TITLE': 'test'})
    def test_create_from_template_success_context(self):
        """
        Should render successfully with context
        """
        mail = Mail.objects.create_from_template(recipient='test@test.com', subject='subject', template='test_context.html', context={'test': 'this_is_a_test_context_variable'})
        self.assertEqual(mail.body, 'context:this_is_a_test_context_variable')

    @override_settings(MAAS={'PROVIDER': 'MAILGUN_V3', 'DEFAULT_SENDER_TITLE': 'test', 'OPTIONS': { 'context_processors': ('project.context_processors.global_context',) }}, )
    def test_create_from_template_context_processors(self):
        """
        Should provide context from context processors
        """
        mail = Mail.objects.create_from_template(recipient='test@test.com', subject='subject', template='test_context_processors.html')
        self.assertEqual(mail.body, 'global_context:this_is_a_test_global_context_variable')