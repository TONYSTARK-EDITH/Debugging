from contextlib import closing
from datetime import timedelta, timezone
import pandas as pd
import pydoodle
from decouple import config
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import connection
from django.db.models import Q
from django.dispatch import receiver
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import requires_csrf_token
import sys
from .models import *

TIME_FORMATTER = "%d.%m.%Y %H:%M:%S"


def bulk_create_query(file):
    query = f"INSERT INTO Interpreter_players (username, password, first_name, email,is_superuser,last_name,is_staff," \
            f"is_active,last_login,date_joined,is_online) VALUES " \
            f"{', '.join(['(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'] * len(file.values))}"
    params = []
    for i in file.values:
        params.extend(
            [i[2].strip(), make_password(i[3].strip(), None, 'md5'), i[0].strip(), i[1].strip(), False, "", True, True,
             None,
             timezone.now(), False])
    with closing(connection.cursor()) as cursor:
        cursor.execute(query, params)


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
    if request.POST.get("logout") == "1":
        AdminPriv.objects.filter(pk=1).update(type="0")
        user.is_online = False
        user.save()


def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("Admin", permanent=True)
        return redirect("Code", permanent=True)
    return render(request, "login.html")


@requires_csrf_token
def login_user(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    auth = authenticate(username=username, password=password)
    if auth is not None:
        AdminPriv.objects.get_or_create(pk=1)
        if not Compiler.objects.filter(pk=1).exists():
            Compiler.objects.create(user_name="max", password="max", client_id=config("CLIENT_ID"),
                                    client_secret_key=config("CLIENT_SECRET_KEY"), selected=True)

        login(request=request, user=auth)
        if request.user.is_superuser:
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
    if not request.user.is_superuser:
        user = Players.objects.get(username=request.user)
        admin = AdminPriv.objects.get(pk=1)
        question_type = admin.type
        end = datetime.strptime(admin.time, TIME_FORMATTER)
        q, res, started, u, t = [], [], "false", [], []
        if question_type != 0:
            q = Questions.objects.filter(question_type=question_type)
            u = user.program_code
            t = user.program_completed
            started = "true"
        name = user.first_name
        for i, j, k in zip(q, u, t):
            t = TestCases.objects.get(question_id=i).testcases
            s = custom_formatter(t)
            res.append([j, i.lang, i.question, s[:2], i.pk, k])
        return render(request, "codeEditor.html",
                      {"res": res, "n": len(res), "name": name, "started": started,
                       "end": end.timestamp(),
                       "count": user.program_completed.count(1)})
    else:
        return redirect("Admin")


def save_utils(user, code, index):
    player = Players.objects.get(username=user)
    lst = player.program_code
    lst[index] = code
    player.program_code = lst
    player.save()


def count_time_utils(user, c_time, index):
    player = Players.objects.get(username=user)
    count = player.program_completed
    timer_player = player.program_time
    if count[index] == 1:
        return
    count[index] = 1
    sub = datetime.strptime(c_time, TIME_FORMATTER)
    s = (datetime.strptime(AdminPriv.objects.get(pk=1).time, TIME_FORMATTER) - sub)
    timer_player[index] = f"{s.seconds}"
    player.program_completed = count
    player.program_time = timer_player
    player.save()


@login_required
@requires_csrf_token
def save_code(request):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax and AdminPriv.objects.get(pk=1).type != "0":
        code = request.POST.get("code")
        index = int(request.POST.get("index"))
        save_utils(request.user, code, index)
        return JsonResponse({})
    else:
        raise Http404()


@login_required
@requires_csrf_token
def get_output(request):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax and AdminPriv.objects.get(pk=1).type != "0":
        code = request.POST.get("code")
        lang = request.POST.get("lang")
        pk_id = int(request.POST.get('id'))
        index = int(request.POST.get("index"))
        timer = datetime.now(pytz.timezone("Asia/Kolkata")).strftime(TIME_FORMATTER)
        save_utils(request.user, code, index)
        test_cases = custom_formatter(TestCases.objects.get(question_id=Questions.objects.get(pk=pk_id)).testcases)
        credentials = Compiler.objects.get(selected=True)
        compiler = pydoodle.Compiler(
            clientId=credentials.client_id,
            clientSecret=credentials.client_secret_key
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
        count_time_utils(request.user, timer, index)
        return JsonResponse({"success": 1, "res": "All test cases have been passed"})
    else:
        raise Http404()


@login_required
@requires_csrf_token
def admin_panel(request):
    if request.user.is_superuser:
        u = Players.objects.all().filter(~Q(pk=1)).order_by("pk")
        results = list(map(lambda x: x.split(","), AdminPriv.objects.get(pk=1).results))
        compiler = [(i.user_name, i.password, i.selected) for i in Compiler.objects.all().order_by('pk')]
        return render(request, "adminPanel.html",
                      {"users": [(player.username, player.is_online, player.first_name) for player in u],
                       "type": AdminPriv.objects.get(pk=1).type, "results": results, "compiler": compiler,
                       "players": AdminPriv.objects.get(pk=1).players_survived})
    else:
        return redirect("Home")


@login_required
@requires_csrf_token
def logout_user(request):
    logout(request=request)
    return redirect("Home", permanent=True)


@login_required
@requires_csrf_token
def user_add(request):
    if request.user.is_superuser:
        fi = pd.read_csv(request.FILES["files"])
        us = [Players(username=i[2].strip(),
                      password=make_password(i[3].strip(), None, 'md5'),
                      first_name=i[0].strip(),
                      email=i[1].strip()) for i in fi.values]
        Players.objects.bulk_create(us, ignore_conflicts=True)
        return redirect("Admin", permanent=True)
    else:
        raise Http404()


@login_required
@requires_csrf_token
def cred_add(request):
    if request.user.is_superuser:
        fi = pd.read_csv(request.FILES["files"])
        us = [Compiler(user_name=i[0], password=i[1], client_id=i[2], client_secret_key=i[3]) for i in fi.values]
        Compiler.objects.bulk_create(us, ignore_conflicts=True)
        return redirect("Admin", permanent=True)
    else:
        raise Http404()


@login_required
@requires_csrf_token
def question_add(request):
    if request.user.is_superuser:
        fi = pd.read_csv(request.FILES["files"])
        questions = [
            Questions(question=i[0], question_code=i[1], question_type=int(i[2]), question_time=int(i[3]),
                      lang=int(i[4]))
            for i in fi.values]
        Questions.objects.bulk_create(questions, ignore_conflicts=True)
        test_cases = [
            TestCases(testcases=i[5], question_id=Questions.objects.get(pk=index)) for index, i in
            enumerate(fi.values, start=1)
        ]
        TestCases.objects.bulk_create(test_cases, ignore_conflicts=True)
        return redirect("Admin", permanent=True)
    else:
        raise Http404()


@login_required
@requires_csrf_token
def start_test(request):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax:
        q_type = request.POST.get("type")
        starter = AdminPriv.objects.get(pk=1)
        starter.type = q_type
        minute = int(q_type) * 10
        # minute = 1 # Debugging purposes
        starter.time = (datetime.now(pytz.timezone("Asia/Kolkata")) + timedelta(minutes=minute)).strftime(
            TIME_FORMATTER)
        starter.save()
        if starter.type != "0":
            codes = [i.question_code for i in Questions.objects.filter(question_type=starter.type)]
            Players.objects.filter(~Q(pk=1)).update(program_code=codes, program_completed=[0] * len(codes),
                                                    program_time=[10000000] * len(codes))
        return JsonResponse({})
    else:
        raise Http404()


@login_required
@requires_csrf_token
def select_compiler(request):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax:
        Compiler.objects.filter(selected=True).update(selected=False)
        Compiler.objects.filter(user_name=request.POST.get("username")).update(selected=True)
        return JsonResponse({})
    else:
        raise Http404()


@login_required
@requires_csrf_token
def select_players(request):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax:
        AdminPriv.objects.filter(pk=1).update(players_survived=request.POST.get("players"))
        return JsonResponse({})
    else:
        raise Http404()


@login_required
@requires_csrf_token
def calculate_results(request):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax:
        lst = list(map(lambda x: (
            x[0].count(1), min(x[1]), x[2], x[3]),
                       Players.objects.filter(~Q(pk=1)).values_list('program_completed', 'program_time', 'username',
                                                                    'first_name', named=True)))
        lst.sort(key=lambda x: (x[0], x[1]), reverse=True)
        length = int(AdminPriv.objects.get(pk=1).players_survived)
        AdminPriv.objects.filter(pk=1).update(results=list(map(lambda x: f"{x[-2]},{x[-1]}", lst[:length])))
        return JsonResponse({})
    else:
        raise Http404()


def delete_user(request):
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    userna = request.POST.get("uname")
    if is_ajax:
        Players.objects.get(username=userna).delete()
        return JsonResponse({})
    else:
        raise Http404()


def handler404(request, exception=None):
    return render(request, template_name="404.html", status=404)


def handler500(request, exception=None):
    type_, value, _ = sys.exc_info()
    return render(request, template_name="500.html", context={"type": repr(type_), "value": value}, status=500)
