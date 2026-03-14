"""
WSGI config for Evalution_of_multiplechoice_Questions_using_AI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Evalution_of_multiplechoice_Questions_using_AI.settings')

application = get_wsgi_application()
