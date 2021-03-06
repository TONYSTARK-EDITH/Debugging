from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from datetime import datetime
from django.db import models
import pytz


def timer():
    return [10000000] * 10


class AdminPriv(models.Model):
    class Meta:
        verbose_name_plural = "AdminPriv"

    class QuestionType(models.IntegerChoices):
        DEF = 0, "Default"
        EAS = 1, "Easy"
        MED = 2, "Medium"
        HIG = 3, "High"

    class ResultNumbers(models.IntegerChoices):
        DEF = 16, "Default"
        EAS = 8, "Easy"
        MED = 4, "Medium"
        S_MED = 2, "High"
        WIN = 1, "Survivor"

    type = models.SmallIntegerField(choices=QuestionType.choices, default=QuestionType.DEF, )
    time = models.CharField(default=f"{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d.%m.%Y %H:%M:%S')}",
                            max_length=1000)
    results = ArrayField(models.CharField(max_length=1000, blank=True), size=16, default=list,
                         blank=True)
    players_survived = models.SmallIntegerField(choices=ResultNumbers.choices, default=ResultNumbers.DEF)


class Players(AbstractUser):
    class Meta:
        verbose_name_plural = "Players"

    is_online = models.BooleanField(default=False)
    program_completed = ArrayField(models.IntegerField(blank=True), size=10, default=list, blank=True)
    program_code = ArrayField(models.TextField(blank=True), size=10, default=list, blank=True)
    program_time = ArrayField(models.IntegerField(), size=10, default=timer, blank=True)


class Questions(models.Model):
    class QuestionType(models.IntegerChoices):
        EAS = 1, "Easy"
        MED = 2, "Medium"
        HIG = 4, "High"

    class QuestionTime(models.IntegerChoices):
        EAS = 1, "10 min"
        MED = 2, "20 min"
        HIG = 4, "30 min"

    class QuestionLang(models.IntegerChoices):
        EAS = 1, "Python"
        MED = 2, "Java"
        HIG = 3, "C"

    question = models.CharField(max_length=1000, default="", blank=True)

    question_code = models.TextField(
        null=False,
        blank=False,
        default=""
    )
    question_type = models.SmallIntegerField(
        choices=QuestionType.choices,
        default=QuestionType.EAS,
        null=False,
        blank=False
    )
    question_time = models.SmallIntegerField(
        choices=QuestionTime.choices,
        default=QuestionTime.EAS,
    )
    lang = models.SmallIntegerField(
        choices=QuestionLang.choices,
        default=QuestionLang.EAS,
    )

    class Meta:
        verbose_name_plural = "Questions"


class TestCases(models.Model):
    testcases = models.TextField(null=False, blank=False)
    question_id = models.ForeignKey(
        'Questions',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = "TestCases"


class Compiler(models.Model):
    class Meta:
        verbose_name_plural = "Compiler"

    user_name = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    client_id = models.CharField(max_length=1000)
    client_secret_key = models.CharField(max_length=1000)
    selected = models.BooleanField(default=False)
