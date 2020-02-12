from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='league-index'),
    path('login', views.login, name='login'),
    path('logout', views.log_out, name='logout'),
    path('create', views.LeagueCreate.as_view(), name='league-create'),
    path('update/<int:pk>', views.LeagueUpdate.as_view(), name='league-update'),
    path('delete/<int:league_id>', views.delete, name='league-delete'),
    path('<int:league_id>', views.detail, name='league-detail'),
    path('join/<slug:token>', views.ArmyCreate.as_view(), name='league-join'),
    path('army/update/<int:pk>', views.ArmyUpdate.as_view(), name='army-update'),
    path('leave/<int:league_id>', views.leave, name='league-leave'),
    path('<int:league_id>/create', views.BattleCreate.as_view(), name='battle-create'),
    path('<int:league_id>/battles', views.battles, name='battle-index'),
    path('battles/delete/<int:battle_id>', views.battle_delete, name='battle-delete'),
    path('battles/update/<int:pk>', views.BattleUpdate.as_view(), name='battle-update'),
]