# Generated by Django 4.0.1 on 2022-03-26 22:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inspections', '0004_inspection_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='completed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='completed_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='failed_inspection',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='inspection',
            name='json',
            field=models.JSONField(blank=True, null=True),
        ),
    ]