from django import forms
from django.utils.translation import ugettext_lazy as _

from contracts.forms import BootstrapForm


class DeputySelectorForm(BootstrapForm):
    SORTING_CHOICES = (('', _('any order')),
                       (_('name'), _('name')),
                       (_('mandates'), _('mandates')))
    SORTING_LOOKUPS = {_('mandates'): '-mandate_count', _('name'): 'name'}

    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': _('filter deputies'),
        'autofocus': 1}))

    sorting = forms.ChoiceField(required=False, widget=forms.Select(
        attrs={'class': 'form-control', 'title': _('order')}), choices=SORTING_CHOICES)
