# Generated by Django 4.2.11 on 2024-03-25 17:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Borrow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('book_id', models.IntegerField()),
                ('borrow_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('due_date', models.DateTimeField()),
                ('returned', models.BooleanField(default=False)),
                ('return_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
