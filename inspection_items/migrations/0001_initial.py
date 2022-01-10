# Generated by Django 4.0 on 2021-12-22 03:21

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0004_alter_user_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='InspectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('inspection_interval', models.TextField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('bi-weekly', 'Bi-Weekly'), ('semi-weekly', 'Semi-Weekly'), ('ten day', '10 Day'), ('monthly', 'Monthly'), ('semi-monthly', 'Semi-Monthly'), ('quarterly', 'Quarterly'), ('annually', 'Annually'), ('semi-annually', 'Semi-Annually'), ('biennial', 'Biennial'), ('triennial', 'Triennial')], max_length=50)),
                ('inspection_type', models.TextField(choices=[('facility', 'Facility'), ('ppe', 'PPE'), ('equipment', 'Equipment'), ('rescue', 'Rescue'), ('first aid', 'First Aid'), ('vehicle', 'Vehicle')], max_length=50)),
                ('serial_number', models.CharField(blank=True, max_length=250, null=True)),
                ('model_number', models.CharField(blank=True, max_length=250, null=True)),
                ('first_inspection_date', models.DateField(blank=True, null=True)),
                ('last_inspection_date', models.DateField(blank=True, null=True)),
                ('next_inspection_date', models.DateField()),
                ('expiration_date', models.DateField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.user')),
            ],
        ),
    ]
