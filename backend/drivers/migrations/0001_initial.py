# Generated by Django 5.2.3 on 2025-06-19 10:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_number', models.CharField(max_length=50, unique=True)),
                ('license_expiry', models.DateField()),
                ('is_verified', models.BooleanField(default=False)),
                ('is_available', models.BooleanField(default=False)),
                ('background_check_status', models.CharField(default='pending', max_length=20)),
                ('current_latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('current_longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('last_location_update', models.DateTimeField(blank=True, null=True)),
                ('vehicle_documents', models.FileField(blank=True, null=True, upload_to='driver_documents/')),
                ('total_earnings', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='driver_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=50)),
                ('year', models.PositiveIntegerField()),
                ('color', models.CharField(max_length=30)),
                ('license_plate', models.CharField(max_length=20, unique=True)),
                ('vehicle_type', models.CharField(choices=[('sedan', 'Sedan'), ('suv', 'SUV'), ('hatchback', 'Hatchback'), ('luxury', 'Luxury'), ('bike', 'Bike')], max_length=20)),
                ('seats', models.PositiveIntegerField(default=4)),
                ('registration_number', models.CharField(max_length=100)),
                ('insurance_expiry', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='drivers.driver')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DriverDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('license', 'Driver License'), ('insurance', 'Insurance Document'), ('registration', 'Vehicle Registration'), ('permit', 'Commercial Permit'), ('background_check', 'Background Check')], max_length=20)),
                ('document_file', models.FileField(upload_to='driver_documents/')),
                ('is_verified', models.BooleanField(default=False)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='drivers.driver')),
            ],
            options={
                'unique_together': {('driver', 'document_type')},
            },
        ),
    ]
