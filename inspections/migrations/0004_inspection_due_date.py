# Generated by Django 4.0.1 on 2022-03-26 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0003_inspectionimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='due_date',
            field=models.DateField(default='1900-01-01'),
            preserve_default=False,
        ),
    ]
