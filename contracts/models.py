import logging
import datetime

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum, Count, Max
from django.db.models.signals import m2m_changed, pre_delete
from django.utils.text import slugify

from treebeard.ns_tree import NS_Node


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Country(models.Model):
    name = models.CharField(max_length=254)


class District(models.Model):
    name = models.CharField(max_length=254)

    base_id = models.IntegerField(unique=True)

    country = models.ForeignKey('Country')


class Category(NS_Node):
    code = models.CharField(max_length=254)
    description_en = models.CharField(max_length=254)
    description_pt = models.CharField(max_length=254)

    def __unicode__(self):
        return '%s' % self.code[:8]

    def get_absolute_url(self):
        return reverse('category', args=[self.pk])

    def _contracts_aggregates(self, flush_cache=False):
        """
        Stores in cache and returns the count and sum of prices of all contracts
        with this and child categories.

        If `flush_cache` is true, the aggregate is re-computed and re-cached.
        """
        cache_name = __name__ + '>_contracts_aggregates' + '>%s' % self.code
        aggregate = cache.get(cache_name)

        if aggregate is None or flush_cache:
            # get ids of all categories child of self (self included)
            categories_ids = list(self.get_tree(self).values_list('id'))

            # construct the aggregate over contracts
            aggregate = Contract.objects.filter(category_id__in=categories_ids)\
                .aggregate(count=Count('id'), price=Sum('price'))

            # hit db
            aggregate = dict(aggregate)

            cache.set(cache_name, aggregate, 60*60*24)

        return aggregate

    def contracts_price(self):
        return self._contracts_aggregates()['price']

    def contracts_count(self):
        return self._contracts_aggregates()['count']

    def compute_data(self):
        self._contracts_aggregates(flush_cache=True)


class Council(models.Model):

    name = models.CharField(max_length=254)

    base_id = models.IntegerField()

    district = models.ForeignKey('District')


class Entity(models.Model):

    name = models.CharField(max_length=254)

    base_id = models.IntegerField(unique=True)

    nif = models.CharField(max_length=254)

    country = models.ForeignKey('Country', null=True)

    def total_earned(self):
        return self.data.total_earned

    def total_expended(self):
        return self.data.total_expended

    def get_base_url(self):
        return 'http://www.base.gov.pt/Base/pt/Pesquisa/Entidade?a=%s' \
               % self.base_id

    def get_absolute_url(self):
        return reverse('entity', args=(self.base_id, slugify(self.name)))

    def get_contracts_ids(self, flush_cache=False):
        """
        Lists all contracts ids the entity participated in.
        The result is cached for 1 month since it is updated using cron.

        Returns a dictionary with keys 'made' and 'set' with the list of
        ids of contracts_made and contract_set respectively.
        """
        cache_name = __name__ + '>contracts_ids' + '>%s' % self.id
        result = cache.get(cache_name)
        if result is None or flush_cache:
            # retrieves the lists.
            result = {'made': list(self.contracts_made.all()
                                   .values_list('id', flat=True)),
                      'set': list(self.contract_set.all()
                                  .values_list('id', flat=True))
                      }
            cache.set(cache_name, result, 60*60*24*30)
        return result

    def get_all_contracts_ids(self):
        ids = self.get_contracts_ids()
        return ids['made'] + ids['set']

    def compute_data(self):
        """
        Computes the data of this entity from the existing relations.
        """
        logger.info('computing data of entity %d', self.base_id)

        # if data does not exist, we create it.
        try:
            self.data
        except EntityData.DoesNotExist:
            self.data = EntityData(entity=self)

        c_set = self.contract_set.aggregate(Sum('price'), Max('signing_date'))
        c_made = self.contracts_made.aggregate(Sum('price'), Max('signing_date'))

        def max_dates(*dates):
            """
            Returns the max of all non-None dates and None if all dates are None.
            """
            dates = list(dates)
            none = datetime.date(1900, 1, 1)

            for index, date in enumerate(dates):
                if date is None:
                    dates[index] = none
            date = max(dates)
            if date == none:
                date = None
            return date

        # update the total earnings and total expenses.
        self.data.total_earned = c_set['price__sum'] or 0
        self.data.total_expended = c_made['price__sum'] or 0

        self.data.last_activity = max_dates(c_set['signing_date__max'],
                                            c_made['signing_date__max'])

        self.data.is_updated = True

        # finish
        self.data.save()

        # update list of contracts on cache
        self.get_contracts_ids(flush_cache=True)

    def main_costumers(self):
        all_costumers = Entity.objects.filter(
            contracts_made__contracted__id=self.id)\
            .distinct().annotate(total_expended=Sum("contracts_made__price"),
                                 total_contracts=Count("contracts_made__price"))\
            .order_by('-total_contracts')[:5]

        all_costumers1 = Entity.objects.filter(
            contract__contractors__id=self.id)\
            .distinct().annotate(total_expended=Sum("contract__price"),
                                 total_contracts=Count("contract__price"))\
            .order_by('-total_contracts')[:5]

        return all_costumers, all_costumers1


class EntityData(models.Model):
    """
    This is a class that contains data from a given entity.
    This data is always computed from existing relations.
    """
    entity = models.OneToOneField('Entity', related_name='data')
    total_earned = models.BigIntegerField(default=0)
    total_expended = models.BigIntegerField(default=0)
    last_activity = models.DateField(default=None, null=True, db_index=True)

    # whether this data is updated
    is_updated = models.BooleanField(default=False)


class ContractType(models.Model):

    base_id = models.IntegerField(unique=True)

    name = models.CharField(max_length=254)


class ProcedureType(models.Model):

    base_id = models.IntegerField(unique=True)

    name = models.CharField(max_length=254)


class ActType(models.Model):

    base_id = models.IntegerField(unique=True)

    name = models.CharField(max_length=254)


class ModelType(models.Model):

    base_id = models.IntegerField(unique=True)

    name = models.CharField(max_length=254)


class ContractManager(models.Manager):
    def get_queryset(self):
        return super(ContractManager, self).get_queryset()\
            .extra(select={'signing_date_is_null': 'signing_date IS NULL'},
                   order_by=['signing_date_is_null', '-signing_date'])


class Contract(models.Model):
    base_id = models.IntegerField(unique=True)
    added_date = models.DateField()
    signing_date = models.DateField(null=True)
    close_date = models.DateField(null=True)
    contract_type = models.ForeignKey('ContractType', null=True)
    procedure_type = models.ForeignKey('ProcedureType', null=True)
    description = models.TextField(null=True)
    contract_description = models.TextField()
    cpvs = models.CharField(max_length=254, null=True)
    category = models.ForeignKey('Category', null=True)
    price = models.BigIntegerField()

    country = models.ForeignKey('Country', null=True)
    district = models.ForeignKey('District', null=True)
    council = models.ForeignKey('Council', null=True)

    contractors = models.ManyToManyField('Entity', related_name='contracts_made')
    contracted = models.ManyToManyField('Entity')

    objects = ContractManager()
    default_objects = models.Manager()

    def get_absolute_url(self):
        return reverse('contract', args=(self.base_id,))

    def get_base_url(self):
        return 'http://www.base.gov.pt/Base/pt/Pesquisa/Contrato?a=%d' \
               % self.base_id


class Tender(models.Model):
    """
    A tender. It contains lots of meta-data, most of them still not used.
    Important data:
    * base_id: the id on the BASE
    * contractors: the entities that started the tender
    * description
    * publication_date: when it was officially published
    * deadline_date: its official deadline date
    * category
    * price
    """
    base_id = models.IntegerField(unique=True)

    contractors = models.ManyToManyField('Entity')

    description = models.TextField()

    model_type = models.ForeignKey('ModelType')
    act_type = models.ForeignKey('ActType')
    contract_type = models.ForeignKey('ContractType', null=True)

    announcement_number = models.CharField(max_length=254)

    publication_date = models.DateField()
    deadline_date = models.DateField()

    cpvs = models.CharField(max_length=254, null=True)
    category = models.ForeignKey('Category', null=True)
    price = models.BigIntegerField()

    dre_url = models.TextField()

    def get_dre_url(self):
        return self.dre_url

    def get_base_url(self):
        return 'http://www.base.gov.pt/Base/pt/Pesquisa/Anuncio?a=%d' \
               % self.base_id

    class Meta:
        ordering = ['-publication_date']


def invalidate_entity_data(sender, instance, **kwargs):
    if sender in [Contract.contractors.through,
                  Contract.contracted.through, Contract]:
        for entity in list(instance.contractors.all()) + \
                list(instance.contracted.all()):
            try:
                entity.data
            except EntityData.DoesNotExist:
                entity.data = EntityData(entity=entity)
            entity.data.is_updated = False
            entity.data.save()


pre_delete.connect(invalidate_entity_data, sender=Contract)

m2m_changed.connect(invalidate_entity_data, sender=Contract.contractors.through)
m2m_changed.connect(invalidate_entity_data, sender=Contract.contracted.through)
