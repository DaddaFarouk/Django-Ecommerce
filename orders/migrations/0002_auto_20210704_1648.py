# Generated by Django 3.1 on 2021-07-04 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='scity',
            new_name='city',
        ),
    ]
