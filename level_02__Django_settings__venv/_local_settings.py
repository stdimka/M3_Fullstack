SECRET_KEY = "*0)qmgv3n1jd5l$%oey-c7_r8t2r$(4etd0yjmqq7%=av_vis1"

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'my_db',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'USER': 'postgres',
        'PASSWORD': '1',
    }
}

