from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE


class Players(models.Model):
    class Meta:
        verbose_name_plural = "Players"

    user = models.OneToOneField(User, related_name="players", on_delete=CASCADE)
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
        default=QuestionType.EAS,
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
