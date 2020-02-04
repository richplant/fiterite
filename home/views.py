from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from sitegate.signin_flows.modern import ModernSignin
from sitegate.signup_flows.classic import ClassicWithEmailSignup

from .models import League, Battle
from .tables import BattleTable
from sitegate.decorators import signup_view, signin_view


@signin_view(flow=ModernSignin,
             template='form_bootstrap',
             widget_attrs={'class': 'form-control', 'placeholder': lambda f: f.label},
             redirect_to='index')
@signup_view(flow=ClassicWithEmailSignup,
             template='form_bootstrap',
             widget_attrs={'class': 'form-control', 'placeholder': lambda f: f.label},
             redirect_to='index')
def login(request):
    return render(request, 'home/login.html', {'title': 'Login or Register'})


@login_required
def index(request):
    league_list = League.objects.order_by('id')[:10]
    context = {'league_list': league_list}
    return render(request, 'home/league_index.html', context)


@login_required
def detail(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    table = BattleTable(Battle.objects.filter(league_id=league_id))
    context = {'league': league,
               'table': table}
    return render(request, 'home/league_detail.html', context)


@login_required
def battles(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    num_battles = Battle.objects.filter(league_id=league_id).count()
    return HttpResponse("League {} contains {} battles".format(league.title, num_battles))
