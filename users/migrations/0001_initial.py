# Generated by Django 3.2.9 on 2021-11-20 12:54

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
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_course', models.IntegerField(default=2)),
                ('active_unit', models.IntegerField(default=1)),
                ('active_concept', models.IntegerField(default=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_view_math3', 'Can View Math 3'), ('can_view_math2', 'Can View Math 2'), ('can_view_math1', 'Can View Math 1')],
            },
        ),
    ]