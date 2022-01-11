# Generated by Django 4.0.1 on 2022-01-10 22:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import inspection_items.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inspection_forms', '0001_initial'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InspectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('inspection_interval', models.TextField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('bi-weekly', 'Bi-Weekly'), ('semi-weekly', 'Semi-Weekly'), ('ten day', '10 Day'), ('monthly', 'Monthly'), ('semi-monthly', 'Semi-Monthly'), ('quarterly', 'Quarterly'), ('annually', 'Annually'), ('semi-annually', 'Semi-Annually'), ('biennial', 'Biennial'), ('triennial', 'Triennial')], max_length=50)),
                ('inspection_type', models.TextField(choices=[('facility', 'Facility'), ('ppe', 'PPE'), ('equipment', 'Equipment'), ('rescue', 'Rescue Equipment'), ('first aid', 'First Aid'), ('vehicle', 'Vehicle'), ('other', 'Other')], max_length=50)),
                ('serial_number', models.CharField(blank=True, max_length=250, null=True)),
                ('model_number', models.CharField(blank=True, max_length=250, null=True)),
                ('first_inspection_date', models.DateField(blank=True, null=True)),
                ('last_inspection_date', models.DateField(blank=True, null=True)),
                ('next_inspection_date', models.DateField()),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('failed_inspection', models.BooleanField(default=False)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to=inspection_items.models.qr_directory_path)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.account')),
                ('assigned_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inspection_forms.inspectionform')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
