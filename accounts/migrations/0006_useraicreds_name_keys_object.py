# Generated by Django 5.1.2 on 2024-11-04 10:43

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_useraicreds'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraicreds',
            name='name_keys_object',
            field=models.CharField(default=django.utils.timezone.now, max_length=120),
            preserve_default=False,
        ),
    ]
