# Generated by Django 3.0.3 on 2020-02-08 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_auto_20200207_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='league',
            name='image',
            field=models.ImageField(upload_to='league'),
        ),
    ]