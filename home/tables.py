import django_tables2 as tables

from .models import Battle


class BattleTable(tables.Table):
    Edit = tables.TemplateColumn('<a class="btn btn-warning" href="{% url "battle-update" record.id %}">Edit</a>')
    Delete = tables.TemplateColumn('<button data-battle-id="{{ record.id }}" data-toggle="modal" data-target="#deleteBattleModal" class="btn btn-danger">Delete</button>')

    class Meta:
        model = Battle
        orderable = False
        template_name = "django_tables2/bootstrap4.html"
        fields = ("date",
                  "army1.user.username",
                  "army1.title",
                  "army1.allegiance",
                  "army1_pts",
                  "army2.user.username",
                  "army2.title",
                  "army2.allegiance",
                  "army2_pts",
                  )
        attrs = {
            "class": "table table-bordered table-hover",
        }


class StandingTable(tables.Table):
    name = tables.Column(orderable=False)
    title = tables.Column(orderable=False)
    allegiance = tables.Column(orderable=False)
    points = tables.Column(orderable=False)

    class Meta:
        order_by = '-points'
        template_name = "django_tables2/bootstrap4.html"

        attrs = {
            "class": "table table-bordered table-hover",
        }
