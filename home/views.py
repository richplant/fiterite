from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
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
             redirect_to='league-index')
@signup_view(flow=ClassicWithEmailSignup,
             template='form_bootstrap',
             widget_attrs={'class': 'form-control', 'placeholder': lambda f: f.label},
             redirect_to='league-index')
def login(request):
    return render(request, 'home/login.html', {'title': 'Login or Register'})


def log_out(request):
    logout(request)
    return redirect('login')


@login_required
def index(request):
    owned_list = League.objects.filter(owner=request.user).order_by('id')
    playing_list = Army.objects.filter(Q(user=request.user) & Q(active=True))
    context = {'owned_list': owned_list, 'playing_list': playing_list}
    return render(request, 'home/league_index.html', context)


@method_decorator(login_required, name='dispatch')
class LeagueCreate(CreateView):
    model = League
    template_name = 'home/league_create.html'
    fields = ['title',
              'current_points',
              'description',
              'image']

    def form_valid(self, form):
        """ Add current user as league owner """
        form.instance.owner = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class LeagueUpdate(UpdateView):
    model = League
    template_name = 'home/league_update.html'
    fields = ['title',
              'current_points',
              'description',
              'image']

    def get_object(self, queryset=None):
        """ Add hook to check league ownership before updating """
        obj = super().get_object(queryset)
        if not obj.owner == self.request.user:
            raise PermissionDenied
        return obj


@method_decorator(login_required, name='dispatch')
class LeagueDelete(DeleteView):
    model = League
    success_url = reverse_lazy('league-index')
    template_name = 'home/league_delete.html'

    def get_object(self, queryset=None):
        """ Add hook to check league ownership before deleting """
        obj = super().get_object(queryset)
        if not obj.owner == self.request.user:
            raise PermissionDenied
        return obj


@login_required
def detail(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    players = [army.user.id for army in Army.objects.filter(league_id=league_id)]
    if league.owner == request.user or request.user.id in players:
        standings = []
        for army in Army.objects.filter(league_id=league_id):
            standings.append({
                'name': army.user.username if army.active else 'RESIGNED',
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
        raise PermissionDenied


@login_required
def battles(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    players = set([army.user.id for army in Army.objects.filter(league_id=league_id)])
    if league.owner == request.user or request.user.id in players:
        num_battles = Battle.objects.filter(league_id=league_id).count()
        return HttpResponse("League {} contains {} battles".format(league.title, num_battles))
    else:
        raise PermissionDenied


@method_decorator(login_required, name='dispatch')
class ArmyCreate(CreateView):
    model = Army
    template_name = 'home/army_create.html'
    fields = ['title',
              'allegiance',
              'image']

    def dispatch(self, request, *args, **kwargs):
        self.league = get_object_or_404(League, password=self.kwargs['token'])
        try:
            existing_army = Army.objects.get(Q(league=self.league) & Q(user=self.request.user))
            existing_army.active = True
            existing_army.save()
            return redirect('league-detail', self.league.id)
        except ObjectDoesNotExist:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['league'] = self.league
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.league = self.league
        form.instance.user = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ArmyUpdate(UpdateView):
    model = Army
    template_name = 'home/army_update.html'
    fields = ['title',
              'allegiance',
              'image']

    def get_object(self, queryset=None):
        """ Add hook to check league ownership before updating """
        obj = super().get_object(queryset)
        if not obj.user == self.request.user:
            raise PermissionDenied
        return obj


@login_required
def leave(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    try:
        existing_army = Army.objects.get(Q(league=league) & Q(user=request.user))
        existing_army.active = False
        existing_army.save()
    except ObjectDoesNotExist:
        pass
    return redirect('league-index')

