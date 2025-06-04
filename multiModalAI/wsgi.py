"""
WSGI config for multiModalAI project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multiModalAI.settings")

application = get_wsgi_application()
>>>>>>> 85d616b3f1ef8af89e277677f2d05b9ac7781bb2
