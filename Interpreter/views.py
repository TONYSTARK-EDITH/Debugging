import pandas as pd
import pydoodle
from decouple import config
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import requires_csrf_token
from .models import *


def custom_formatter(string: str) -> list:
    input_s = string.strip().split("\n")
    tes = []
    i = 0
    while i < len(input_s):
        if "Input:" == input_s[i].strip() or "Input :" == input_s[i].strip():
            i += 1
            tes.append([])
            while i < len(input_s):
                if "Output:" == input_s[i].strip() or "Output :" == input_s[i].strip():
                    break
                if len(tes[-1]) == 0:
                    tes[-1] = [input_s[i]]
                else:
                    tes[-1][0] += f"\n{input_s[i].strip()}"
                i += 1
        else:
            i += 1
            while i < len(input_s):
                if "Input:" == input_s[i].strip() or "Input :" == input_s[i].strip():
                    break
                if len(tes[-1]) == 1:
                    tes[-1].append(input_s[i])
                else:
                    tes[-1][1] += f"\n{input_s[i]}"
                i += 1
    return tes


@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):
    user.is_online = True
    user.save()


@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):
    user.is_online = False
    user.save()


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
        AdminPriv.objects.get_or_create(pk=1)
        login(request=request, user=auth)
        if "tony" in username:
            return redirect("Admin", permanent=True)
        return redirect("Code", permanent=True)
    else:
        messages.error(request, f"The user {username} is not authenticated")
        return redirect("Home", permanent=True)


def compare_testcases(output, testcases):
    return output.strip() == testcases.strip()


@login_required
@requires_csrf_token
def code_editor(request):
    q = Questions.objects.filter(question_type=AdminPriv.objects.get(pk=1).type)
    res = []
    name = Players.objects.get(username=request.user).first_name
    for i in q:
        t = TestCases.objects.get(question_id=i).testcases
        s = custom_formatter(t)
        res.append([i.question_code, i.lang, i.question, s[:2]])
    return render(request, "codeEditor.html",
                  {"res": res, "n": len(res), "name": name})


@login_required
@requires_csrf_token
def get_output(request):
    if request.is_ajax():
        code = request.POST.get("code")
        lang = request.POST.get("lang")
        pk_id = int(request.POST.get('id'))
        test_cases = custom_formatter(TestCases.objects.get(question_id=Questions.objects.get(pk=pk_id)).testcases)
        compiler = pydoodle.Compiler(
            clientId=config("CLIENT_ID"),
            clientSecret=config("CLIENT_SECRET_KEY")
        )
        base_cases = []
        is_base_case_fails = False
        for Input, Output in test_cases[:2]:
            result = compiler.execute(script=code, language=lang, stdIn=Input)
            output = "\n".join(result.output)
            if not compare_testcases(output, Output):
                is_base_case_fails = True
            base_cases.append(output)
        if is_base_case_fails:
            return JsonResponse({"success": -2, "res": "Base test cases failed", "base": base_cases})

        for Input, Output in test_cases[2:]:
            result = compiler.execute(script=code, language=lang, stdIn=Input)
            output = "\n".join(result.output)
            if not compare_testcases(output, Output):
                return JsonResponse({"success": -1, "res": "Private test cases failed"})
        return JsonResponse({"success": 1, "res": "All test cases have been passed"})
    else:
        pass


@login_required
@requires_csrf_token
def admin_panel(request):
    u = Players.objects.all().filter(~Q(pk=1))
    return render(request, "adminPanel.html",
                  {"users": [(player.username, player.is_online, player.first_name) for player in u]})


@login_required
@requires_csrf_token
def logout_user(request):
    logout(request=request)
    return redirect("Home", permanent=True)


@login_required
@requires_csrf_token
def user_add(request):
    fi = pd.read_csv(request.FILES["files"])
    us = [Players(username=i[2].strip(),
                  password=make_password(i[3].strip()),
                  first_name=i[0].strip(),
                  email=i[1].strip()) for i in fi.values]
    Players.objects.bulk_create(us, ignore_conflicts=True)
    return redirect("Admin", permanent=True)


@login_required
@requires_csrf_token
def question_add(request):
    fi = pd.read_csv(request.FILES["files"])
    questions = [
        Questions(question=i[0], question_code=i[1], question_type=int(i[2]), question_time=int(i[3]), lang=int(i[4]))
        for i in fi.values]
    Questions.objects.bulk_create(questions, ignore_conflicts=True)
    test_cases = [
        TestCases(testcases=i[5], question_id=Questions.objects.get(pk=index + 1)) for index, i in enumerate(fi.values)
    ]
    TestCases.objects.bulk_create(test_cases, ignore_conflicts=True)
    return redirect("Admin", permanent=True)
