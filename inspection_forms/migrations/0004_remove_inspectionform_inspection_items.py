# Generated by Django 4.0 on 2021-12-22 03:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inspection_forms', '0003_alter_inspectionform_inspection_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspectionform',
            name='inspection_items',
        ),
    ]
