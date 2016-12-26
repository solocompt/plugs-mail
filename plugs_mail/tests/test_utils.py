"""
Testing Mail Utils
"""

from mock import patch

from django.test import TestCase

from plugs_mail.mail import PlugsMail
from plugs_mail.management.commands import load_email_templates

template = 'SUBJECT: Subject line!\n' \
           '\n' \
           '{% extends "base.html" %}\n' \
           '{% block content %}\n' \
           '<p>Hello,</p>\n' \
           '<p>Test Message.</p>\n' \
           '{% endblock %}\n'


class TestEmailClass(PlugsMail):
    template = 'TEMPLATE_NAME'
    context = ('User', )
    description = 'Email description ...'

class TestUtils(TestCase):
    """
    Testing Mail Utils
    """

    def test_create_text_template_from_html_version(self):
        """
        Ensures a template text version is created from the html version
        """
        html_template = '<p>Bacon ipsum dolor amet <b>picanha</b> bacon ribeye <i>salami</i> meatloaf beef</p>'
        command = load_email_templates.Command()
        result = command.text_version(html_template)
        self.assertEqual(result, 'Bacon ipsum dolor amet picanha bacon ribeye salami meatloaf beef\n\n')


    def test_email_class_context_not_found_exception(self):
        """
        Ensures exception raised when context not found during email creation
        """
        mail = TestEmailClass()
        with self.assertRaisesMessage(Exception, 'Context Not Found'):
            mail.send('example@example.com')


    def test_email_template_missing_exception(self):
        """
        Ensures exception raised when template attr is missing from the email class
        """
        del TestEmailClass.template
        with self.assertRaisesMessage(AssertionError, 'Must set template attribute on subclass.'):
            mail = TestEmailClass()


    def test_email_cannot_have_duplicate_context_objects(self):
        """
        Ensures exception raise if email class has duplicate context objects
        """
        class DuplicateContextEmailClass(PlugsMail):
            template = 'TEMPLATE_NAME'
            context = ('User', 'User')

        # exercise and assert
        msg = 'Cannot have duplicated context objects.'
        with self.assertRaisesMessage(Exception, msg):
            mail = DuplicateContextEmailClass()


    def test_email_class_description_not_required(self):
        """
        Ensures email class description not required
        """
        del TestEmailClass.description
        mail = TestEmailClass()
        self.assertIsInstance(mail, PlugsMail)


    def test_email_class_does_not_require_context(self):
        """
        Ensures email class does not require context
        """
        del TestEmailClass.context
        mail = TestEmailClass()
        mail.send('example@example.com')


    def test_raise_exception_if_template_language_is_missing(self):
        """
        Ensures exception raised of template file is missing language code
        """
        command = load_email_templates.Command()
        file_ = '/var/www/src/plugs-auth/plugs_auth/templates/emails/account_activated.html'
        with self.assertRaisesMessage(Exception, 'Template file must end in ISO_639-1 language code.'):
            language = command.get_template_language(file_)


    def test_email_language_determined_from_template_file(self):
        """
        Ensures template language is determined from template file
        """
        command = load_email_templates.Command()
        file_ = '/var/www/src/plugs-auth/plugs_auth/templates/emails/account_activated_pt.html'
        language = command.get_template_language(file_)
        self.assertEqual(language, 'pt')


    def test_email_subject_determined_from_template(self):
        """
        Ensures template subject is determined from template content
        """
        command = load_email_templates.Command()
        subject = command.get_subject(template)
        self.assertEqual(subject, 'Subject line!')


    def test_email_content_determined_from_template(self):
        """
        Ensures template content is determined from template content
        """
        command = load_email_templates.Command()
        html_content = command.get_html_content(template)
        expected = '{% extends "base.html" %}\n' \
                   '{% block content %}\n' \
                   '<p>Hello,</p>\n' \
                   '<p>Test Message.</p>\n' \
                   '{% endblock %}\n'
        self.assertEqual(html_content, expected)
