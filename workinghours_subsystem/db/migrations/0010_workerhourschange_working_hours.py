# Generated by Django 2.2 on 2020-01-18 02:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0009_auto_20200118_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerhourschange',
            name='working_hours',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='worker_hours_change', to='db.WorkerHours'),
        ),
    ]