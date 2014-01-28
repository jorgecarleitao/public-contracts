import set_up
set_up.set_up_django_environment()

from datetime import date
from deputies import models

legislatures = [[6, date(year=1991, month=11, day=04), date(year=1995, month=10, day=24)],
                [7, date(year=1995, month=10, day=27), date(year=1999, month=10, day=24)],
                [8, date(year=1999, month=10, day=25), date(year=2002, month=4, day=4)],
                [9, date(year=2002, month=4, day=5), date(year=2005, month=3, day=9)],
                [10, date(year=2005, month=03, day=10), date(year=2009, month=10, day=14)],
                [11, date(year=2009, month=10, day=15), date(year=2011, month=06, day=19)],
                [12, date(year=2011, month=06, day=20), None]]


for legislature in legislatures:
    try:
        models.Legislature.objects.get(number=legislature[0])
    except models.Legislature.DoesNotExist:
        models.Legislature.objects.create(number=legislature[0],
                                          date_start=legislature[1],
                                          date_end=legislature[2])

parties = ["PSD", "PS", "PCP", "BE", "PEV", "CDS-PP", "PSN"]

for party in parties:
    try:
        models.Party.objects.get(abbrev=party)
    except models.Party.DoesNotExist:
        models.Party.objects.create(abbrev=party)
