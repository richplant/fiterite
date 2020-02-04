from django.utils import timezone
from django.conf import settings
from django.db import models


class League(models.Model):
    title = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    image = models.ImageField()
    password = models.CharField(max_length=20, blank=False, null=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Army(models.Model):
    title = models.CharField(max_length=128)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    BOC = "BOC"
    KRN = "KRN"
    NUR = "NUR"
    SKN = "SKN"
    SLA = "SLA"
    TZN = "TZN"
    STD = "STD"
    LON = "LON"
    NGT = "NGT"
    OBR = "OBR"
    FEC = "FEC"
    BCR = "BCR"
    GSG = "GSG"
    OGR = "OGR"
    ORK = "ORK"
    COS = "COS"
    DOK = "DOK"
    FYR = "FYR"
    IDK = "IDK"
    KRO = "KRO"
    SER = "SER"
    SCE = "SCE"
    SYL = "SYL"

    ALLEGIANCE_CHOICES = (
        (BOC, "Beasts of Chaos"),
        (KRN, "Khorne"),
        (NUR, "Nurgle"),
        (SKN, "Skaven"),
        (SLA, "Slaanesh"),
        (TZN, "Tzeentch"),
        (STD, "Slaves to Darkness"),
        (LON, "Legions of Nagash"),
        (NGT, "Nighthaunt"),
        (OBR, "Ossiarch Bonereapers"),
        (FEC, "Flesh Eater Courts"),
        (BCR, "Beastclaw Raiders"),
        (GSG, "Gloomspite Gitz"),
        (OGR, "Ogor Mawtribes"),
        (ORK, "Orruk Warclans"),
        (COS, "Cities of Sigmar"),
        (DOK, "Daughters of Khaine"),
        (FYR, "Fyreslayers"),
        (IDK, "Idoneth Deepkin"),
        (KRO, "Kharadron Overlords"),
        (SER, "Seraphon"),
        (SCE, "Stormcast Eternals"),
        (SYL, "Sylvaneth"),
    )

    allegiance = models.CharField(
        max_length=3,
        choices=ALLEGIANCE_CHOICES,
        default=BOC,
        verbose_name="Allegiance"
    )

    def __str__(self):
        return self.title


class Battle(models.Model):
    date = models.DateField(blank=False, null=False, default=timezone.now, verbose_name="Date")
    league = models.ForeignKey(League, on_delete=models.CASCADE, default=None)
    army1 = models.ForeignKey(
        Army,
        related_name="your_army",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    army2 = models.ForeignKey(
        Army,
        related_name="other_player_army",
        on_delete=models.CASCADE,
        blank=False,
        null=False
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
