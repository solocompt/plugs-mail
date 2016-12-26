"""
Plugs Mail
"""

import logging

from post_office import mail
from post_office.models import EmailTemplate

from plugs_core import utils

from plugs_mail.settings import app_settings


LOGGER = logging.getLogger(__name__)


class PlugsMail(object):
    """
    Solo mail is the class responsible for
    getting and validating the context and
    prepare the email for sending
    """
    template = None
    context = None
    context_data = {}
    data = None

    def __init__(self):
        self.validate_context()
        assert self.template, 'Must set template attribute on subclass.'

    def validate_context(self):
        """
        Make sure there are no duplicate context objects
        or we might end up with switched data

        Converting the tuple to a set gets rid of the
        eventual duplicate objects, comparing the length
        of the original tuple and set tells us if we
        have duplicates in the tuple or not
        """
        if self.context and len(self.context) != len(set(self.context)):
            LOGGER.error('Cannot have duplicated context objects')
            raise Exception('Cannot have duplicated context objects.')

    def get_instance_of(self, model_cls):
        """
        Search the data to find a instance
        of a model specified in the template
        """
        for obj in self.data.values():
            if isinstance(obj, model_cls):
                return obj
        LOGGER.error('Context Not Found')
        raise Exception('Context Not Found')

    def get_context(self):
        """
        Create a dict with the context data
        context is not required, but if it
        is defined it should be a tuple
        """
        if not self.context:
            return
        else:
            assert isinstance(self.context, tuple), 'Expected a Tuple not {0}'.format(type(self.context))
        for model in self.context:
            model_cls = utils.get_model_class(model)
            key = utils.camel_to_snake(model_cls.__name__)
            self.context_data[key] = self.get_instance_of(model_cls)

    def get_extra_context(self):
        """
        Override this method if you want to provide
        extra context. The extra_context must be a dict.
        Be very careful no validation is being performed.
        """
        return {}


    def get_context_data(self):
        """
        Context Data is equal to context + extra_context
        Merge the dicts context_data and extra_context and
        update state
        """
        self.get_context()
        self.context_data.update(self.get_extra_context())
        return self.context_data

    def send(self, to, language=None, **data):
        """
        This is the method to be called
        """
        self.data = data
        self.get_context_data()
        if app_settings['SEND_EMAILS']:
            try:
                if language:
                    mail.send(to, template=self.template, context=self.context_data, language=language)
                else:
                    mail.send(to, template=self.template, context=self.context_data)
            except EmailTemplate.DoesNotExist:
                msg = 'Trying to use a non existent email template {0}'.format(self.template)
                LOGGER.error('Trying to use a non existent email template {0}'.format(self.template))
