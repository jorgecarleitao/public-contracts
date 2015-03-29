from django import forms
from django.utils.translation import ugettext_lazy as _

from contracts.forms import BootstrapForm, DateRangeField


class LawSelectorForm(BootstrapForm):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': _('filter laws'),
        'autofocus': 1}))

    range = DateRangeField(required=False, widget=forms.TextInput(attrs={
        'placeholder': _('date range'), 'class': 'form-control datepicker'}))

    def add_prefix(self, field_name):
        # HACK: ensures 'search' is translated.
        if field_name == 'search':
            return _('search')
        if field_name == 'range':
            return _('range')
        return _(field_name)
