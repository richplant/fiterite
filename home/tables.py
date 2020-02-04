import django_tables2 as tables
from .models import Battle


class BattleTable(tables.Table):
    class Meta:
        model = Battle
        template_name = "django_tables2/bootstrap4.html"
        fields = ("date",
                  "army1.title",
                  "army1.allegiance",
                  "army1.user.username",
                  "army1_pts",
                  "army2.title",
                  "army2.allegiance",
                  "army2.user.username",
                  "army2_pts",
                  )
