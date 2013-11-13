from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _
import views


urlpatterns = patterns('',
                       url(r'^$', views.home, name='contracts_home'),
                       url(r'^%s$' % _('contracts'), views.contracts_list, name='contracts_list'),
                       url(r'^%s$' % _('categories'), views.categories_list, name='categories_list'),
                       url(r'^%s$' % _('entities'), views.entities_list, name='entities_list'),
                       url(r'^%s/(\d+)$' % _('category'), views.category_view, name='category_view'),
                       url(r'^%s$' % _('entities-category-ranking'), views.entities_category_ranking, name='entities_category_ranking'),
                       url(r'^%s$' % 'entities-json', views.entities_category_ranking_json, name='category_ranking_index_json')
                       )
