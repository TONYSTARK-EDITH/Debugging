from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class AdminPriv(models.Model):
    class Meta:
        verbose_name_plural = "AdminPriv"

    class QuestionType(models.IntegerChoices):
        DEF = 0, "Default"
        EAS = 1, "Easy"
        MED = 2, "Medium"
        HIG = 3, "High"

    type = models.SmallIntegerField(choices=QuestionType.choices, default=QuestionType.DEF, )
    time = models.CharField(default="", max_length=1000)


class Players(AbstractUser):
    class Meta:
        verbose_name_plural = "Players"

    is_online = models.BooleanField(default=False)
    program_completed = ArrayField(models.IntegerField(null=True, blank=True), size=10, default=[0] * 10)
    program_code = ArrayField(models.TextField(null=True, blank=True), size=10, default=[""] * 10)
    program_time = ArrayField(models.CharField(default="", null=True, max_length=1000), size=10, default=[""] * 10)


class Questions(models.Model):
    class QuestionType(models.IntegerChoices):
        EAS = 1, "Easy"
        MED = 2, "Medium"
        HIG = 3, "High"

    class QuestionTime(models.IntegerChoices):
        EAS = 1, "10 min"
        MED = 2, "20 min"
        HIG = 3, "30 min"

    class QuestionLang(models.IntegerChoices):
        EAS = 1, "Python"
        MED = 2, "Java"
        HIG = 3, "C"

    question = models.CharField(max_length=1000, default="")

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
