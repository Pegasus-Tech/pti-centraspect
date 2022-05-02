import os
from urllib.parse import urlparse

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ALLOWED_HOSTS = ['*']
APP_HOST_URL = 'https://www.centraspect.io'

CENTRASPECT_FROM_EMAIL = os.environ.get('CENTRA_FROM_EMAIL')
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_SANDBOX_MODE_IN_DEBUG = False

AWS_STORAGE_BUCKET_NAME = 'pti-qr-codes'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_REGION_NAME = 'us-east-2'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
S3_USE_SIGV4 = True
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ADDRESSING_STYLE = 'virtual'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MAX_IMAGE_SIZE = (500, 500)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('APP_SECRET')
ADMIN_USER_PW = os.environ.get('CENTRA_ADMIN_USER_PW')
AUTH_TOKEN_EXPIRY = os.environ.get('AUTH_TOKEN_EXPIRY') or 60 * 60

url = urlparse(os.environ.get("REDIS_URL"))
Q_CLUSTER = {
    'name': 'centraspect',
    'workers': 8,
    'recycle': 500,
    'timeout': 60,
    'compress': True,
    'save_limit': 250,
    'queue_limit': 500,
    'cpu_affinity': 1,
    'redis': {
        'host': url.hostname,
        'port': url.port,
        'db': 0,
        'username': url.username,
        'password': url.password,
        'ssl': True,
        'ssl_ca_certs': None,
        'ssl_cert_reqs': None
    }
}


WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True
