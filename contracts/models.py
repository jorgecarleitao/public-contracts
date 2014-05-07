from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum, Count
from django.utils.text import slugify
from treebeard.ns_tree import NS_Node


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

    def _own_contracts_aggregate(self, flush_cache=False):
        cache_name = __name__ + '>_own_contracts_aggregate' + '>%s' % self.code
        aggregate = cache.get(cache_name)
        if aggregate is None or flush_cache:
            aggregate = dict(self.contract_set.aggregate(Sum('price'), Count('price')))
            cache.set(cache_name, aggregate, 60*60*24)
        return aggregate

    def own_contracts_count(self):
        return self._own_contracts_aggregate()['price__count']

    def own_contracts_price(self):
        return self._own_contracts_aggregate()['price__sum']

    def _contracts_aggregate(self, flush_cache=False):
        cache_name = __name__ + '>_contracts_aggregate' + '>%s' % self.code
        aggregate = cache.get(cache_name)
        if aggregate is None or flush_cache:
            categories = self.get_tree(self)
            aggregate = dict(categories.aggregate(count=Count("contract__id"), price_sum=Sum("contract__price")))
            cache.set(cache_name, aggregate, 60*60*24)
        return aggregate

    def contracts_price(self):
        return self._contracts_aggregate()['price_sum']

    def contracts_count(self):
        return self._contracts_aggregate()['count']

    def compute_data(self):
        self._contracts_aggregate(flush_cache=True)
        self._own_contracts_aggregate(flush_cache=True)


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

    def get_contracts_ids(self, flush_cache=False):
        """
        Retrieves a list of all contracts' ids the entity participated in.
        The result is cached for 1 month because it is updated on server side using cron.
        """
        cache_name = __name__ + '>contracts_ids' + '>%s' % self.id
        result = cache.get(cache_name)
        if result is None or flush_cache:
            # retrieves the list. This is an expensive query.
            result = list(self.contract_set.all().values_list('id', flat=True)) + \
                     list(self.contracts_made.all().values_list('id', flat=True))
            cache.set(cache_name, result, 60*60*24*30)
        return result

    def last_contracts(self, slice_value=None):
        query = Contract.objects.filter(id__in=self.get_contracts_ids())

        if slice_value is None:
            return query

        try:
            return query[:slice_value]
        except IndexError:
            return query

    def __unicode__(self):
        return self.name

    def get_base_url(self):
        return 'http://www.base.gov.pt/base2/html/pesquisas/entidades.shtml#%s' % self.base_id

    def get_absolute_url(self):
        return reverse('entity', args=(self.id, slugify(self.name)))

    def count_contracts(self):
        return self.contracts_made.count()

    def count_contracts_received(self):
        return self.contract_set.count()

    def add_contract_as_contracted(self, contract):
        self.data.total_earned += contract.price
        self.data.save()

    def add_contract_as_contractor(self, contract):
        self.data.total_expended += contract.price
        self.data.save()

    def compute_data(self):
        """
        Computes the data of this entity from the existing relations.
        """
        print('computing data of entity %d' % self.base_id)

        # if data does not exist, we create it.
        try:
            self.data
        except EntityData.DoesNotExist:
            self.data = EntityData(entity=self)

        # we update the total earnings and total expenses.
        self.data.total_earned = self.contract_set.aggregate(Sum('price'))['price__sum'] or 0
        self.data.total_expended = self.contracts_made.aggregate(Sum('price'))['price__sum'] or 0
        self.data.save()

        # update list of contracts
        self.get_contracts_ids(flush_cache=True)


class EntityData(models.Model):
    """
    This is a class that contains data from a given entity.
    This data is always computed from existing relations.
    """
    entity = models.OneToOneField('Entity', related_name='data')
    total_earned = models.BigIntegerField(default=0)
    total_expended = models.BigIntegerField(default=0)


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


class Contract(models.Model):
    base_id = models.IntegerField(unique=True)
    added_date = models.DateField()
    signing_date = models.DateField(null=True)
    close_date = models.DateField(null=True)
    contract_type = models.ForeignKey('ContractType', null=True)
    procedure_type = models.ForeignKey('ProcedureType', null=True)
    description = models.TextField(null=True)
    contract_description = models.TextField()
    cpvs = models.CharField(max_length=254)
    category = models.ForeignKey('Category', null=True)
    price = models.BigIntegerField()

    country = models.ForeignKey('Country', null=True)
    district = models.ForeignKey('District', null=True)
    council = models.ForeignKey('Council', null=True)

    contractors = models.ManyToManyField('Entity', related_name='contracts_made')
    contracted = models.ManyToManyField('Entity')

    def get_absolute_url(self):
        return reverse('contract', args=(self.id,))

    def get_base_url(self):
        return 'http://www.base.gov.pt/base2/html/pesquisas/contratos.shtml#%d' % self.base_id

    def get_first_contractor(self):
        # there are at least two contracts with errors in the official database,
        # which leads to 0 contractors. These contracts don't have any information.
        try:
            return self.contractors.all()[0]
        except IndexError:
            return None

    def get_first_contracted(self):
        # there are at least two contracts with errors in the official database,
        # which leads to 0 contracted. These contracts don't have any information.
        try:
            return self.contracted.all()[0]
        except IndexError:
            return None

    class Meta:
        ordering = ['-signing_date']


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

    description = models.CharField(max_length=254)
    model_type = models.ForeignKey('ModelType')
    act_type = models.ForeignKey('ActType')
    contract_type = models.ForeignKey('ContractType', null=True)

    announcement_number = models.CharField(max_length=254)

    publication_date = models.DateField()
    deadline_date = models.DateField()

    cpvs = models.CharField(max_length=254)
    category = models.ForeignKey('Category', null=True)
    price = models.BigIntegerField()

    dre_number = models.IntegerField()
    dre_series = models.IntegerField()
    dre_document = models.IntegerField()

    def get_dre_url(self):
        return 'http://dre.pt/util/getpdf.asp?s=udrcp&serie=%d&data=%s&iddr=%d&iddip=%d' %\
               (self.dre_series,
                self.publication_date.strftime('%Y-%m-%d'),
                self.dre_number,
                self.dre_document)

    def get_base_url(self):
        return 'http://www.base.gov.pt/base2/html/pesquisas/anuncios.shtml#%d' % self.base_id

    class Meta:
        ordering = ['-publication_date']
