from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='league-index'),
    path('login', views.login, name='login'),
    path('create', views.LeagueCreate.as_view(), name='league-create'),
    path('update', views.LeagueUpdate.as_view(), name='league-update'),
    path('delete', views.LeagueDelete.as_view(), name='league-delete'),
    path('<int:league_id>', views.detail, name='league-detail'),
    path('<int:league_id>/battles', views.battles, name='battles'),
]