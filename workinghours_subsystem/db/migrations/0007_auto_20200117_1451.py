# Generated by Django 2.2 on 2020-01-17 06:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0006_auto_20200117_1438'),
    ]

    operations = [
        migrations.RenameField(
            model_name='approverecode',
            old_name='change_date',
            new_name='approve_submit_date',
        ),
    ]
