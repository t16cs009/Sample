# Generated by Django 2.1.1 on 2019-01-23 06:29

import datetime
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=150, verbose_name='登録者')),
                ('summary', models.CharField(blank=True, max_length=50, verbose_name='備考')),
                ('start_time', models.TimeField(default=datetime.time(7, 0), verbose_name='開始時間')),
                ('end_time', models.TimeField(default=datetime.time(7, 0), verbose_name='終了時間')),
                ('date', models.DateField(verbose_name='日付')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('noon_numbers', models.IntegerField(blank=True, default=0, verbose_name='昼シフト人数')),
                ('night_numbers', models.IntegerField(blank=True, default=0, verbose_name='夜シフト人数')),
            ],
        ),
    ]
