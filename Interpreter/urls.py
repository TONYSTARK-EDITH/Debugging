from django.contrib import admin
from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.home, name="Home"),
    path("login", v.login_user, name="Login"),
    path("home", v.code_editor, name="Code"),
    path("adm", v.admin_panel, name="Admin"),
    path("logout", v.logout_user, name="Logout"),
    path("addUser", v.user_add, name="Adduser"),
    path("addQuestion", v.question_add, name="Questionadd"),
    path("run", v.get_output, name="Run"),
]
