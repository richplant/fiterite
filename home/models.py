from uuid import uuid4

from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class League(models.Model):
    title = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to='league', blank=False, null=False)
    password = models.UUIDField(blank=False, null=False, default=uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_points = models.PositiveIntegerField(blank=False, null=False, default=500)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('league-detail', args=[str(self.id)])


class Allegiance(models.TextChoices):
    BOC = "BOC", _("Beasts of Chaos")
    KRN = "KRN", _("Khorne")
    NUR = "NUR", _("Nurgle")
    SKN = "SKN", _("Skaven")
    SLA = "SLA", _("Slaanesh")
    TZN = "TZN", _("Tzeentch")
    STD = "STD", _("Slaves to Darkness")
    LON = "LON", _("Legions of Nagash")
    NGT = "NGT", _("Nighthaunt")
    OBR = "OBR", _("Ossiarch Bonereapers")
    FEC = "FEC", _("Flesh Eater Courts")
    BCR = "BCR", _("Beastclaw Raiders")
    GSG = "GSG", _("Gloomspite Gitz")
    OGR = "OGR", _("Ogor Mawtribes")
    ORK = "ORK", _("Orruk Warclans")
    COS = "COS", _("Cities of Sigmar")
    DOK = "DOK", _("Daughters of Khaine")
    FYR = "FYR", _("Fyreslayers")
    IDK = "IDK", _("Idoneth Deepkin")
    KRO = "KRO", _("Kharadron Overlords")
    SER = "SER", _("Seraphon")
    SCE = "SCE", _("Stormcast Eternals")
    SYL = "SYL", _("Sylvaneth")


class Army(models.Model):
    title = models.CharField(max_length=128)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='army', blank=False, null=False)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    active = models.BooleanField(default=True, blank=False, null=False)

    allegiance = models.CharField(
        max_length=3,
        choices=Allegiance.choices,
        default=Allegiance.BOC,
        verbose_name="Allegiance"
    )

    def __str__(self):
        return self.title

    def get_points_for(self):
        battles = Battle.objects.filter(league_id=self.league)
        pts1 = [battle.army1_pts for battle in battles if battle.army1 == self]
        pts2 = [battle.army2_pts for battle in battles if battle.army2 == self]
        return sum(pts1) + sum(pts2)

    def get_absolute_url(self):
        return reverse('league-detail', args=[str(self.league.id)])


class Battle(models.Model):
    date = models.DateField(blank=False, null=False, default=timezone.now, verbose_name="Date")
    league = models.ForeignKey(League, on_delete=models.CASCADE, default=None)
    army1 = models.ForeignKey(
        Army,
        related_name="your_army",
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )
    army2 = models.ForeignKey(
        Army,
        related_name="other_player_army",
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )
    army1_pts = models.PositiveIntegerField(blank=False, null=False, verbose_name="Points")
    army2_pts = models.PositiveIntegerField(blank=False, null=False, verbose_name="Points")

    def __str__(self):
        return "{} vs {}".format(self.army1.title, self.army2.title)

    def get_winner_id(self):
        if self.army1_pts == self.army2_pts:
            return False
        else:
            return self.army1 if self.army1_pts > self.army2_pts else self.army2
