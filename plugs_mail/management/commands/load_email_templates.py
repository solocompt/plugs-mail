import os
import inspect
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_module

from post_office import models

from plugs_core import utils
from plugs_mail.mail import PlugsMail
from plugs_mail.settings import app_settings as plugs_mail_settings


class Command(BaseCommand):

    overrides = {}

    def handle(self, *args, **options):
        self.override_default_templates()
        templates = self.get_apps()
        count = self.create_templates(templates)
        if count:
            self.stdout.write(self.style.SUCCESS('Successfully loaded %s email templates' % count))
        else:
            self.stdout.write(self.style.SUCCESS('No email templates to load'))

    def override_default_templates(self):
        """
        Override the default emails already defined by other apps
        """
        if plugs_mail_settings['OVERRIDE_TEMPLATE_DIR']:
            dir_ = plugs_mail_settings['OVERRIDE_TEMPLATE_DIR']
            for file_ in os.listdir(dir_):
                if file_.endswith(('.html', 'txt')):
                    self.overrides[file_] = dir_

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
                templates += self.get_plugs_mail_classes(app)
            except ImportError:
                pass
        return templates

    def get_members(self, app):
        return inspect.getmembers(app)

    def get_templates_files_in_dir(self, dir_):
        return os.listdir(dir_)

    def get_template_files(self, location, class_name):
        """
        Multilanguage support means that for each template
        we can have multiple templtate files, this methods
        returns all the template (html and txt) files
        that match the (class) template name
        """
        template_name = utils.camel_to_snake(class_name)
        dir_ = location[:-9] + 'templates/emails/'
        files_ = []
        for file_ in self.get_templates_files_in_dir(dir_):
            if file_.startswith(template_name) and file_.endswith(('.html', '.txt')):
                if file_ in self.overrides:
                    files_.append(self.overrides[file_] + file_)
                else:
                    files_.append(dir_ + file_)
        return files_

    def get_plugs_mail_classes(self, app):
        """
        Returns a list of tuples, but it should
        return a list of dicts
        """
        classes = []
        members = self.get_members(app)
        for member in members:
            name, cls = member
            if inspect.isclass(cls) and issubclass(cls, PlugsMail) and name != 'PlugsMail':
                files_ = self.get_template_files(app.__file__, name)
                for file_ in files_:
                    try:
                        description = cls.description
                        location = file_
                        language = self.get_template_language(location)
                        classes.append((name, location, description, language))
                    except AttributeError:
                        raise AttributeError('Email class must specify email description.')
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
            # TODO naive and temp implementation
            # check if the two chars correspond to one of the
            # available languages
            raise Exception('Template file must end in ISO_639-1 language code.')
        return language_code.lower()

    def get_subject(self, text):
        """
        Email template subject is the first
        line of the email template, we can optionally
        add SUBJECT: to make it clearer
        """
        first_line = text.splitlines(True)[0]
        # TODO second line should be empty
        if first_line.startswith('SUBJECT:'):
            subject = first_line[len('SUBJECT:'):]
        else:
            subject = first_line
        return subject.strip()

    def get_html_content(self, text):
        """
        Parse content and return html
        """
        lines = text.splitlines(True)
        return ''.join(lines[2:])

    def create_templates(self, templates):
        """
        Gets a list of templates to insert into the database
        """
        count = 0
        for template in templates:
            if not self.template_exists_db(template):
                name, location, description, language = template
                text = self.open_file(location)
                html_content = self.get_html_content(text)
                data = {
                    'name': utils.camel_to_snake(name).upper(),
                    'html_content': html_content,
                    'content': self.text_version(html_content),
                    'subject': self.get_subject(text),
                    'description': description,
                    'language': language
                }
                if models.EmailTemplate.objects.create(**data):
                    count += 1
        return count


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
        Receives a template and checks if it exists in the database
        using the template name and language
        """
        name = utils.camel_to_snake(template[0]).upper()
        language = utils.camel_to_snake(template[3])
        try:
            models.EmailTemplate.objects.get(name=name, language=language)
        except models.EmailTemplate.DoesNotExist:
            return False
        return True
