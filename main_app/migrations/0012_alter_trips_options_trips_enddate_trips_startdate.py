# Generated by Django 4.2.4 on 2023-08-26 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_alter_trips_options_remove_trips_enddate_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trips',
            options={'ordering': ['-startDate']},
        ),
        migrations.AddField(
            model_name='trips',
            name='endDate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='trips',
            name='startDate',
            field=models.DateField(null=True),
        ),
    ]
