from django.urls import path
from . import views

app_name = "data"
urlpatterns=[
  path("", views.home, name="home"),
  path("submit/", views.submit_contact, name="submit_contact"),
  path("delete/<person_id>", views.delete_contact, name="delete_contact")
]