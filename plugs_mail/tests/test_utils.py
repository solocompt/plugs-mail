""" 
Testing Mail Utils
"""

from django.test import TestCase

from plugs_mail.management.commands import load_email_templates

class TestUtils(TestCase):

    def test_create_text_template_from_html_version(self):
        """
        Ensures a template text version is created from the html version
        """
        html_template = '<p>Bacon ipsum dolor amet <b>picanha</b> bacon ribeye <i>salami</i> meatloaf beef</p>'
        command = load_email_templates.Command()
        result = command.text_version(html_template)
        self.assertEqual(result, 'Bacon ipsum dolor amet picanha bacon ribeye salami meatloaf beef\n\n')        
