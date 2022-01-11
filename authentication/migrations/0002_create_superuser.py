from django.db import migrations, models
import django.db.models.deletion
from django.contrib.auth.hashers import make_password
from centraspect.settings import ADMIN_USER_PW

def create_initial_account(apps, schema_editor):
    Account = apps.get_model('authentication', 'Account')
    User = apps.get_model('authentication', 'User')

    acct = Account.objects.create (
        name='Centraspect Admin'
    )

    User.objects.create(
        username='89webdev@gmail.com',
        email='89webdev@gmail.com',
        first_name='Justin',
        last_name='Dodson',
        password=make_password(ADMIN_USER_PW),
        is_superuser=True,
        is_staff=True,
        is_active=True,
        account=acct
    )

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_account)
    ]