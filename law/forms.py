from django import forms
from django.utils.translation import ugettext_lazy as _

from contracts.forms import BootstrapForm


class LawSelectorForm(BootstrapForm):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': _('filter laws'),
        'autofocus': 1}))
