# Generated by Django 2.2 on 2020-01-19 02:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0011_auto_20200118_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerhours',
            name='project_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='wh_project_id', to='db.Project'),
        ),
    ]