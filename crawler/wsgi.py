"""
WSGI config for crawler project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

Parent_Dir = os.path.dirname( os.path.dirname(__file__) )
sys.path.append(Parent_Dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crawler.settings")

application = get_wsgi_application()
