from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.client_list_view, name="client_list"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("client_create/", views.client_create_view, name="client_create"),
    path("client/edit/<int:client_id>/", views.client_edit, name="client_edit"),
    path("run_script", views.run_script, name="run_script"),
]