from django.contrib import sitemaps
from django.core.urlresolvers import reverse

priorities = {'contracts_home': 1.0,
              'deputies_home': 1.0,
              'law_home': 1.0,
              'about': 0.5}


class ContractsSitemap(sitemaps.Sitemap):

    def items(self):
        return [view for view in priorities]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return priorities[item]
