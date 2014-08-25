from django import forms
from django.utils.translation import ugettext_lazy as _


class DateRangeField(forms.DateField):

    def to_python(self, value):
        if not value:
            return None
        values = value.split(' - ')
        from_date = super(DateRangeField, self).to_python(values[0])
        to_date = super(DateRangeField, self).to_python(values[1])
        return from_date, to_date


class BootstrapForm(forms.Form):

    def as_div(self):
        """
        Returns this form rendered as HTML <div>s.
        """
        return self._html_output(
            normal_row='<div class="form-group">%(label)s %(field)s</div>',
            error_row='%s',
            row_ender='</div>',
            help_text_html='',
            errors_on_separate_row=True)


class ContractSelectorForm(BootstrapForm):
    CHOICES = ((_('date'), _('date')),
               (_('price'), _('price')))
    SORTING_LOOKUPS = {_('date'): '-signing_date', _('price'): '-price'}

    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': _('filter contracts')}))

    sorting = forms.ChoiceField(required=False, widget=forms.Select(
        attrs={'class': 'form-control', 'title': _('order')}), choices=CHOICES)

    range = DateRangeField(required=False, widget=forms.TextInput(
        attrs={'placeholder': _('date range'),
               'class': 'form-control datepicker'}))

    def add_prefix(self, field_name):
        # HACK: ensures 'range' is translated.
        if field_name == 'range':
            return _('range')
        return _(field_name)


class TenderSelectorForm(ContractSelectorForm):
    CHOICES = ((_('date'), _('date')),
               (_('price'), _('price')))
    SORTING_LOOKUPS = {_('date'): '-publication_date', _('price'): '-price'}

    search = forms.CharField(required=False,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control',
                                        'placeholder': _('filter tenders')}))


class EntitySelectorForm(BootstrapForm):
    CHOICES = ((_('earnings'), _('earnings')),
               (_('expenses'), _('expenses')))
    SORTING_LOOKUPS = {_('earnings'): '-data__total_earned',
                       _('expenses'): '-data__total_expended'}

    search = forms.CharField(required=False,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control',
                                        'placeholder': _('filter entities')}))

    sorting = forms.ChoiceField(required=False, widget=forms.Select(
        attrs={'class': 'form-control', 'title': _('order')}), choices=CHOICES)

    def add_prefix(self, field_name):
        return _(field_name)
