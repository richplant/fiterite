from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django_tables2 import SingleTableView
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


@login_required
def delete(request, league_id):
    league = get_object_or_404(League, id=league_id)
    if not league.owner == request.user:
        raise PermissionDenied
    league.delete()
    return redirect('league-index')


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
        last_battles = Battle.objects.filter(league_id=league_id).order_by('-date')[:10]
        battle_table = BattleTable(list(last_battles))
        context = {'league': league,
                   'battle_table': battle_table,
                   'standing_table': standing_table}
        return render(request, 'home/league_detail.html', context)
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
        try:
            self.league = League.objects.get(password=self.kwargs['token'])
        except (ValidationError, ObjectDoesNotExist):
            messages.error(request, "No league found for that token.", extra_tags='join-league')
            return redirect('league-index')
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


@login_required
def battles(request, league_id):
    league = get_object_or_404(League, pk=league_id)
    players = set([army.user.id for army in Army.objects.filter(league=league) if army.active])
    if not league.owner == request.user and not request.user.id in players:
        raise PermissionDenied
    battle_table = BattleTable(Battle.objects.filter(league=league).order_by('-date'))
    context = {
        'battle_table': battle_table
    }
    return render(request, 'home/battles.html', context)


@method_decorator(login_required, name='dispatch')
class BattleCreate(CreateView):
    model = Battle
    template_name = 'home/battle_create.html'
    fields = ['date',
              'army1_pts',
              'army2',
              'army2_pts']

    def dispatch(self, request, *args, **kwargs):
        self.league = get_object_or_404(League, id=self.kwargs['league_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(BattleCreate, self).get_form(form_class)
        form.fields['army2'].queryset = Army.objects.filter(Q(league=self.league) & ~Q(user=self.request.user))
        return form

    def get_context_data(self, **kwargs):
        kwargs['league'] = self.league
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.army1 = Army.objects.get(Q(league=self.league) & Q(user=self.request.user))
        form.instance.league = self.league
        return super().form_valid(form)


@login_required
def battle_delete(request, battle_id):
    battle = get_object_or_404(Battle, id=battle_id)
    league = League.objects.get(id=battle.league.id)
    if not battle.army1.user == request.user \
            and not battle.army2.user == request.user \
            and not league.owner == request.user:
        raise PermissionDenied
    battle.delete()
    return redirect('battle-index', league.id)


@method_decorator(login_required, name='dispatch')
class BattleUpdate(UpdateView):
    model = Battle
    template_name = 'home/battle_update.html'
    fields = ['date',
              'army1_pts',
              'army2',
              'army2_pts']

    def dispatch(self, request, *args, **kwargs):
        battle = get_object_or_404(Battle, id=self.kwargs['pk'])
        self.league = get_object_or_404(League, id=battle.league.id)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(BattleUpdate, self).get_form(form_class)
        form.fields['army2'].queryset = Army.objects.filter(Q(league=self.league) & ~Q(user=self.request.user))
        return form


def faq(request):
    return render(request, 'home/faq.html')
