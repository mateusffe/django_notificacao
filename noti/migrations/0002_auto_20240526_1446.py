# Generated by Django 3.1.4 on 2024-05-26 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noti', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacao',
            name='codigo_verificador',
            field=models.PositiveIntegerField(default=58381727, primary_key=True, serialize=False, unique=True),
        ),
    ]