# Generated by Django 2.0.8 on 2019-05-22 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modello', '0088_auto_20190426_0900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contatto',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
