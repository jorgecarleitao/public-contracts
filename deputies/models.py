from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max


class Deputy(models.Model):
    """
    A deputy.
    """
    official_id = models.IntegerField()
    name = models.CharField(max_length=254)
    birthday = models.DateField(null=True)  # some deputies don't have birthday info.

    party = models.ForeignKey("Party", null=True)  # the current party, updated on legislatures

    is_active = models.BooleanField(default=False)  # if the deputy's last mandate is on the current legislature.

    def __unicode__(self):
        return 'deputy ' + self.name

    def get_absolute_url(self):
        return 'http://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%d' % self.official_id

    def update(self):
        mandate = self.mandate_set.all()[:1].get()
        if mandate.legislature.number == Legislature.objects.all().aggregate(max=Max("number"))['max']:
            self.is_active = True
        else:
            self.is_active = False
        self.party = mandate.party
        self.save()

    def get_image_url(self):
        return 'http://app.parlamento.pt/webutils/getimage.aspx?id=%d&type=deputado' % self.official_id

    class Meta:
        ordering = ['name']


class Party(models.Model):
    """
    A Party
    """
    abbrev = models.CharField(max_length=20)

    def get_absolute_url(self):
        return reverse('party_view', args=[self.pk])

    def __unicode__(self):
        return self.abbrev


class Legislature(models.Model):
    """
    A period between two elections.
    """
    number = models.PositiveIntegerField()

    date_start = models.DateField()
    date_end = models.DateField(null=True)  # if it haven't finished yet, it is null.

    def __unicode__(self):
        return self.number


class Mandate(models.Model):
    """
    A mandate of a deputy within a legislature.
    He must be set by a party and from a constituency
    """
    deputy = models.ForeignKey(Deputy)
    legislature = models.ForeignKey(Legislature)
    district = models.ForeignKey('contracts.District', null=True)  # null if outside Portugal
    party = models.ForeignKey(Party)

    # he can leave or enter in the middle of the legislature
    date_start = models.DateField()
    date_end = models.DateField(null=True)  # if it haven't finished yet, it is null.

    def __unicode__(self):
        return '%s (%s - %s)' % (self.deputy.name, self.legislature, self.party.abbrev)

    class Meta:
        ordering = ['-legislature__number']
