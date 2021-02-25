# Generated by Django 2.2.19 on 2021-02-25 11:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FacebookProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('facebook_account_id', models.BigIntegerField(unique=True)),
                ('primary_access_token', models.TextField()),
                ('oauth_access_token', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='facebook_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
