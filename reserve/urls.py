from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("base/", views.base, name="base"),
    path("dashboard/", views.dashboard, name="dashboard"),

    #path("reserve/", views.reserve, name="reserve"),
    
]