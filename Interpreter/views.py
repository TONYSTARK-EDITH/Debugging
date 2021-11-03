import pandas as pd
import pydoodle
from decouple import config
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models import Q
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token

from .models import *


@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):
    user.players.is_online = True
    user.players.save()


@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):
    user.players.is_online = False
    user.players.save()


def home(request):
    if request.user.is_authenticated:
        if "tony" in str(request.user):
            return redirect("Admin", permanent=True)
        return redirect("Code", permanent=True)
    return render(request, "login.html")


def login_user(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    auth = authenticate(username=username, password=password)
    if auth is not None:
        Players.objects.get_or_create(user=User.objects.get(pk=1))
        login(request=request, user=auth)
        if "tony" in username:
            return redirect("Admin", permanent=True)
        return redirect("Code", permanent=True)
    else:
        messages.error(request, f"The user {username} is not authenticated")
        return redirect("Home", permanent=True)


@login_required
@requires_csrf_token
def code_editor(request):
    q = Questions.objects.get(pk=1)
    return render(request, "codeEditor.html", {"code": q.question_code, "lang": q.lang, "question": q.question})


@login_required
@requires_csrf_token
def get_output(request):
    if request.is_ajax():
        code = request.POST("code")
        lang = request.POST("lang")
        compiler = pydoodle.Compiler(
            clientId=config("CLIENT_ID"),
            clientSecret=config("CLIENT_SECRET_KEY")
        )
        result = compiler.execute(script=code, language=lang)
        usage = compiler.usage()
    else:
        pass


@login_required
@requires_csrf_token
def admin_panel(request):
    u = Players.objects.all().filter(~Q(user=User.objects.get(pk=1)))
    return render(request, "adminPanel.html", {"users": [(player.user.username, player.is_online) for player in u]})


@login_required
@requires_csrf_token
def logout_user(request):
    logout(request=request)
    return redirect("Home", permanent=True)


@login_required
@requires_csrf_token
def user_add(request):
    fi = pd.read_csv(request.FILES["files"])
    for i in fi.values:
        tmp = User.objects.create_user(
            username=i[2].strip(),
            password=i[3].strip(),
            first_name=i[0].strip(),
            email=i[1].strip()
        )
        tmp.save()
        Players.objects.get_or_create(user=tmp)
    return redirect("Admin", permanent=True)


@login_required
@requires_csrf_token
def question_add(request):
    fi = pd.read_csv(request.FILES["files"])
    lst = [
        Questions(question=i[0], question_code=i[1], question_type=int(i[2]), question_time=int(i[3]), lang=int(i[4]))
        for i in fi.values]
    Questions.objects.bulk_create(lst, ignore_conflicts=True)
    return redirect("Admin", permanent=True)
