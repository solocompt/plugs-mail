=====
Usage
=====

To use Plugs Mail in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'plugs_mail.apps.PlugsMailConfig',
        ...
    )

Add Plugs Mail's URL patterns:

.. code-block:: python

    from plugs_mail import urls as plugs_mail_urls


    urlpatterns = [
        ...
        url(r'^', include(plugs_mail_urls)),
        ...
    ]
