# Generated by Django 2.1.5 on 2019-03-07 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bakerySystem', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'customer'), (2, 'owner'), (3, 'staff'), (4, 'admin')], default=4),
        ),
    ]