from django.contrib import sitemaps
from django.core.urlresolvers import reverse

priorities = {'contracts_home': 1.0,
              'contracts_list': 0.9,
              'entities_list': 0.9,
              'categories_list': 0.9,
              'contracts_about': 0.5}


class ContractsSitemap(sitemaps.Sitemap):

    def items(self):
        return [view for view in priorities]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return priorities[item]
