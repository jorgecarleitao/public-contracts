from django.db import models


class Deputy(models.Model):
    """
    A deputy.
    """
    official_id = models.IntegerField()
    name = models.CharField(max_length=254)
    birthday = models.DateField(null=True)  # some deputies don't have birthday info.

    occupation = models.CharField(blank=True, max_length=254)

    commissions = models.TextField(blank=True, max_length=5000)
    education = models.TextField(blank=True, max_length=5000)
    current_jobs = models.TextField(blank=True, max_length=5000)
    jobs = models.TextField(blank=True, max_length=5000)
    awards = models.TextField(blank=True, max_length=5000)

    def __unicode__(self):
        return 'deputy ' + self.shortname

    class Meta:
        ordering = ['name']


class Party(models.Model):
    """
    A Party
    """
    abbrev = models.CharField(max_length=20)

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
    district = models.ForeignKey('contracts.District', null=True) # null if outside portugal
    party = models.ForeignKey(Party)

    # he can leave or enter in the middle of the legislature
    date_begin = models.DateField()
    date_end = models.DateField(null=True)  # if it haven't finished yet, it is null.

    def __unicode__(self):
        return '%s (%s - %s)' % (self.deputy.shortname, self.legislature, self.party.abbrev)

    class Meta:
        ordering = ['-legislature__number']
