import datetime
from django.db import models
from django.utils import timezone


class Schedule(models.Model):
    """スケジュール"""
    user_name = models.CharField('登録者', max_length=150)
    summary = models.CharField('備考', max_length=50, blank=True)
    start_time = models.TimeField('開始時間', default=datetime.time(7, 0, 0))
    night_start_time = models.TimeField('夜シフト開始時間', default=datetime.time(17, 0, 0))
    end_time = models.TimeField('終了時間', default=datetime.time(7, 0, 0))
    date = models.DateField('日付')
    created_at = models.DateTimeField('作成日', default=timezone.now)
    noon_numbers = models.IntegerField('昼シフト人数', default=0, blank=True)
    night_numbers = models.IntegerField('夜シフト人数', default=0, blank=True)

    # created_at = models.DateTimeField('作成日', default=timezone.now)
    # noon_numbers = models.IntegerField('昼シフト人数', default=0, blank=True)
    # night_numbers = models.IntegerField('夜シフト人数', default=0, blank=True)


    def __str__(self):
        return self.summary

class Decision(models.Model):
    date = models.DateField('日付')
    noon_numbers = models.IntegerField('昼シフト人数', default=0, blank=True)
    night_numbers = models.IntegerField('夜シフト人数', default=0, blank=True)

    def __str__(self):
        return models.Model.__str__(self)