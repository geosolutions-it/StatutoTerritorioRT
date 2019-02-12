HOSTNAME='localhost' \
DJANGO_SETTINGS_MODULE='base.settings.settings' \
DJANGO_ALLOWED_HOSTS='127.0.0.1 localhost' \
DJANGO_DEBUG='True' \
DJANGO_SECRET_KEY='79yvc9j1j_sr6!0$o3^g)&yph!8nzv$t7*3p3xk88abl7=gnyy' \
DJANGO_DATABASE_URL='postgres://serapide:serapide@localhost:5432/serapide' \
DJANGO_PUBLIC_URL='http://127.0.0.1:8000' \
EMAIL_ENABLE='True' \
DEFAULT_FROM_EMAIL='Portale del Territorio <no-reply@serapide.it>' \
DJANGO_EMAIL_HOST='localhost' \
DJANGO_EMAIL_HOST_USER='' \
DJANGO_EMAIL_HOST_PASSWORD='' \
DJANGO_EMAIL_USE_SSL='False' \
DJANGO_EMAIL_PORT=25 python manage.py $@
