# Generated by Django 4.0.1 on 2022-03-28 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0006_alter_inspection_completed_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='missed_inspection',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
