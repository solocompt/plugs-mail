import inspect
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_module

from post_office import models

from plugs_core import utils
from plugs_mail.mail import PlugsMail


class Command(BaseCommand):

    def handle(self, *args, **options):
        templates = self.get_apps()
        self.create_templates(templates)

    def get_apps(self):
        """
        Get the list of installed apps
        and return the apps that have
        an emails module
        """
        templates = []
        for app in settings.INSTALLED_APPS:
            try:
                app = import_module(app + '.emails')
                templates += self.get_plugs_mail_subs(app)
            except ImportError:
                pass
        return templates

    def get_members(self, app):
        return inspect.getmembers(app)

    def get_plugs_mail_subs(self, app):
        """
        Returns a list of tuples, but it should
        return a list of dicts
        """
        classes = []
        members = self.get_members(app)
        for member in members:
            name, cls = member
            if inspect.isclass(cls) and issubclass(cls, PlugsMail) and name != 'PlugsMail':
                try:
                    subject = cls.subject
                    description = cls.description
                    location = app.__file__
                    classes.append((name, location, subject, description))
                except AttributeError:
                    raise AttributeError('Email class must specify email subject and description.')
        return classes

    def get_template_language(self, file_):
        """
        Return the template language
        Every template file must end in
        with the language code, and the 
        code must match the ISO_6301 lang code
        https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        valid examples:

        account_created_pt.html
        payment_created_en.txt
        """
        stem = Path(file_).stem
        language_code = stem.split('_')[-1:][0]
        if len(language_code) != 2:
            # naive and temp implementation
            # check if the two chars correspond to one of the
            # available languages
            raise Exception('Template file must end in ISO_639-1 language code.')
        return language_code.lower()

    def create_templates(self, templates):
        """
        Gets a list of templates to insert into the database
        """
        for template in templates:
            name, location, subject, description = template
            if not self.template_exists_db(name):
                # create template if it does not exists
                # if does not exist, try to find a default template
                dir_ = location[:-9] + 'templates/emails/'
                file_ = dir_ + utils.camel_to_snake(name) + '.html'

                text = self.open_file(file_)
                data = {
                    'name': utils.camel_to_snake(name).upper(),
                    'html_content': text,
                    'content': self.text_version(text),
                    'subject': subject,
                    'description': description,
                    'language': self.get_template_language(file_)
                }
                models.EmailTemplate.objects.create(**data)

    def text_version(self, html):
        """
        Uses util to create a text email template
        from a html one
        """
        return utils.html_to_text(html)

    def open_file(self, file_):
        """
        Receives a file path has input and returns a
        string with the contents of the file
        """
        with open(file_, 'r', encoding='utf-8') as file:
            text = ''
            for line in file:
                text += line
        return text

    def template_exists_db(self, template):
        """
        Receives a template name and sees if it exists in the database
        """
        template = utils.camel_to_snake(template).upper()
        try:
            models.EmailTemplate.objects.get(name=template)
        except models.EmailTemplate.DoesNotExist:
            return False
        return True
