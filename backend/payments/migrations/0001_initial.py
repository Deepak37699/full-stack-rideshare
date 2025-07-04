# Generated by Django 5.2.3 on 2025-06-19 10:36

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rides', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverEarnings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gross_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('platform_commission', models.DecimalField(decimal_places=2, max_digits=8)),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tip_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('is_paid_out', models.BooleanField(default=False)),
                ('paid_out_at', models.DateTimeField(blank=True, null=True)),
                ('payout_transaction_id', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='earnings', to=settings.AUTH_USER_MODEL)),
                ('ride', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='driver_earnings', to='rides.ride')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method_type', models.CharField(choices=[('card', 'Credit/Debit Card'), ('paypal', 'PayPal'), ('apple_pay', 'Apple Pay'), ('google_pay', 'Google Pay'), ('cash', 'Cash')], max_length=20)),
                ('is_default', models.BooleanField(default=False)),
                ('card_number', models.CharField(blank=True, max_length=255)),
                ('cardholder_name', models.CharField(blank=True, max_length=100)),
                ('expiry_month', models.PositiveIntegerField(blank=True, null=True)),
                ('expiry_year', models.PositiveIntegerField(blank=True, null=True)),
                ('external_id', models.CharField(blank=True, max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'method_type', 'external_id')},
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('payment_type', models.CharField(choices=[('ride_fare', 'Ride Fare'), ('tip', 'Tip'), ('refund', 'Refund'), ('cancellation_fee', 'Cancellation Fee'), ('driver_payout', 'Driver Payout')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=255)),
                ('gateway_response', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('failed_at', models.DateTimeField(blank=True, null=True)),
                ('failure_reason', models.TextField(blank=True)),
                ('refund_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('refunded_at', models.DateTimeField(blank=True, null=True)),
                ('ride', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='rides.ride')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to=settings.AUTH_USER_MODEL)),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.paymentmethod')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('reason', models.CharField(choices=[('ride_cancelled', 'Ride Cancelled'), ('driver_no_show', 'Driver No Show'), ('poor_service', 'Poor Service'), ('overcharge', 'Overcharge'), ('technical_issue', 'Technical Issue'), ('other', 'Other')], max_length=20)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('approved', 'Approved'), ('processed', 'Processed'), ('rejected', 'Rejected')], default='requested', max_length=20)),
                ('external_refund_id', models.CharField(blank=True, max_length=255)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True)),
                ('payment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='refund', to='payments.payment')),
                ('processed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_refunds', to=settings.AUTH_USER_MODEL)),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
