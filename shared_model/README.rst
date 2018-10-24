============
Shared Model
============

Shared Model is a simple Django app to share a model between apps.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "shared_model" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'shared_model',
    ]

2. Run `python manage.py migrate` to create the model models.

3. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a model (you'll need the Admin app enabled).