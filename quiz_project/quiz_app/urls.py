from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("history/", views.history, name="history"),
    path("quiz/<int:quiz_id>/", views.quiz_detail, name="quiz_detail"),
    path("quiz/<int:quiz_id>/download/json/", views.download_json, name="quiz_download_json"),
    path("quiz/<int:quiz_id>/download/md/", views.download_markdown, name="quiz_download_md"),
    path("quiz/<int:quiz_id>/delete/", views.delete_quiz, name="quiz_delete"),
]
