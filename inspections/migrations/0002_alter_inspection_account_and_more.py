# Generated by Django 4.0.1 on 2022-01-10 22:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inspection_forms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inspection_items', '0001_initial'),
        ('authentication', '0001_initial'),
        ('inspections', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='authentication.account'),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='completed_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inspection_forms.inspectionform'),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inspection_items.inspectionitem'),
        ),
    ]
