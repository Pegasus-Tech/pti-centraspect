# Generated by Django 4.0.1 on 2022-04-04 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inspection_forms', '0001_initial'),
        ('inspections', '0007_inspection_missed_inspection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='inspection_forms.inspectionform'),
        ),
    ]
