from django.conf.urls import patterns, url

from . import contract_views

urlpatterns = patterns('',
                       url(r'id(\d+)', contract_views.main_view, name='contract'),
                       url(r'(\d+)', contract_views.redirect_id),
                       )
