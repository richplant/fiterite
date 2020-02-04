from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('<int:league_id>', views.detail, name='detail'),
    path('<int:league_id>/battles', views.battles, name='battles')
]