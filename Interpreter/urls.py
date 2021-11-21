from django.urls import path
from . import views as v

urlpatterns = [
    path("", v.home, name="Home"),
    path("login", v.login_user, name="Login"),
    path("home", v.code_editor, name="Code"),
    path("adm", v.admin_panel, name="Admin"),
    path("logout", v.logout_user, name="Logout"),
    path("addUser", v.user_add, name="Adduser"),
    path("addQuestion", v.question_add, name="Addquestions"),
    path("run", v.get_output, name="Run"),
    path("start", v.start_test, name="Start"),
    path("save", v.save_code, name="Save"),
    path("cred_add", v.cred_add, name="Credadd"),
    path("selector", v.select_compiler, name="Credentials"),
    path("players", v.select_players, name="Players"),
    path("results", v.calculate_results, name="Results")
]
