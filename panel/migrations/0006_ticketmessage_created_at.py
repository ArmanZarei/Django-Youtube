# Generated by Django 3.2.14 on 2022-08-02 12:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0005_auto_20220801_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketmessage',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]