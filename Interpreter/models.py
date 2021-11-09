from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django_sharding_library.models import ShardedByMixin


class AdminPriv(models.Model):
    class QuestionType(models.IntegerChoices):
        EAS = 1, "Easy"
        MED = 2, "Medium"
        HIG = 3, "High"

    type = models.SmallIntegerField(choices=QuestionType.choices, default=QuestionType.EAS, )
    started = models.BooleanField(default=False)


class Players(AbstractUser, ShardedByMixin):
    class Meta:
        verbose_name_plural = "Players"

    is_online = models.BooleanField(default=False)


class Questions(models.Model):
    class QuestionType(models.IntegerChoices):
        EAS = 1, "Easy"
        MED = 2, "Medium"
        HIG = 3, "High"

    class QuestionTime(models.IntegerChoices):
        EAS = 1, "15 min"
        MED = 2, "25 min"
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
