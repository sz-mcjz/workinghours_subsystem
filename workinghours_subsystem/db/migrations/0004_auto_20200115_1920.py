# Generated by Django 2.2 on 2020-01-15 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0003_auto_20200115_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerhours',
            name='entry_data',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='workerhours',
            name='pname',
            field=models.CharField(max_length=125),
        ),
        migrations.AlterField(
            model_name='workerhours',
            name='writer',
            field=models.CharField(max_length=125),
        ),
    ]
