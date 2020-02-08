from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView
from sitegate.signin_flows.modern import ModernSignin
from sitegate.signup_flows.classic import ClassicWithEmailSignup

from .models import League, Battle, Army, Allegiance
from .tables import BattleTable, StandingTable
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
    owned_list = League.objects.filter(owner=request.user).order_by('id')
    playing_list = League.objects.filter(army__user=request.user).exclude(owner=request.user)
    context = {'owned_list': owned_list, 'playing_list': playing_list}
    return render(request, 'home/league_index.html', context)


@method_decorator(login_required, name='dispatch')
class LeagueCreate(CreateView):
    model = League
    template_name = 'home/league_create.html'
    fields = ['title',
              'password',
              'current_points',
              'description',
              'image']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class LeagueUpdate(UpdateView):
    model = League
    template_name = 'home/league_update.html'


@method_decorator(login_required, name='dispatch')
class LeagueDelete(DeleteView):
    model = League
    success_url = reverse_lazy('index')


@login_required
def detail(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    players = [army.user.id for army in Army.objects.filter(league_id=league_id)]
    if league.owner == request.user or request.user.id in players:
        standings = []
        for army in Army.objects.filter(league_id=league_id):
            standings.append({
                'name': army.user.username,
                'title': army.title,
                'allegiance': Allegiance(army.allegiance).label,
                'points': army.get_points_for(),
            })
        standing_table = StandingTable(standings)
        standing_table.order_by = '-points'
        battle_table = BattleTable(Battle.objects.filter(league_id=league_id)[:10])
        context = {'league': league,
                   'battle_table': battle_table,
                   'standing_table': standing_table}
        return render(request, 'home/league_detail.html', context)
    else:
        raise HttpResponseForbidden("You can only view leagues you are part of.")


@login_required
def battles(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    players = set([army.user.id for army in Army.objects.filter(league_id=league_id)])
    if league.owner == request.user or request.user.id in players:
        num_battles = Battle.objects.filter(league_id=league_id).count()
        return HttpResponse("League {} contains {} battles".format(league.title, num_battles))
    else:
        raise HttpResponseForbidden("You can only view battles for league you are part of.")
