from django.contrib import admin

from . import models
# Register your models here.
admin.site.register(models.Questions)
admin.site.register(models.TestCases)
admin.site.register(models.Players)