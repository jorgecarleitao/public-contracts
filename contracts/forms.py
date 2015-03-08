from django import forms
from django.utils.translation import ugettext_lazy as _


class DateRangeField(forms.DateField):

    def to_python(self, value):
        if not value:
            return None
        values = value.split(' - ')
        from_date = super(DateRangeField, self).to_python(values[0])

        if len(values) > 1:
            to_date = super(DateRangeField, self).to_python(values[1])
        else:
            # if no range, use equal dates
            to_date = from_date
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
    SORTING_CHOICES = (('', _('any order')),
                       (_('earnings'), _('earnings')),
                       (_('expenses'), _('expenses')))
    SORTING_LOOKUPS = {_('earnings'): '-data__total_earned',
                       _('expenses'): '-data__total_expended'}

    LISTS_CHOICES = (('', _('any entity')), (_('municipality'), _('municipality')),
                     (_('county'), _('county')))
    LISTS_MAP = {
        _('municipality'): 'municipality',
        _('county'): 'county'}

    search = forms.CharField(required=False,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control',
                                        'placeholder': _('filter entities')}))

    type = forms.ChoiceField(required=False, widget=forms.Select(
        attrs={'class': 'form-control', 'title':
            _('limits list to specific entities')}), choices=LISTS_CHOICES)

    sorting = forms.ChoiceField(required=False, widget=forms.Select(
        attrs={'class': 'form-control', 'title': _('order')}), choices=SORTING_CHOICES)

    def add_prefix(self, field_name):
        # HACK: ensures 'type' is translated.
        if field_name == 'type':
            return _('type')
        return _(field_name)

    def __init__(self, *args, **kwargs):
        """
        Required so we can override the field `sorting`.
        """
        super(EntitySelectorForm, self).__init__(*args, **kwargs)
        self.fields['sorting'].choices = self.SORTING_CHOICES


class CostumerSelectorForm(EntitySelectorForm):

    SORTING_CHOICES = (('', _('any order')),
                       (_('contracts'), _('contracts')),
                       (_('value'), _('value')))
    SORTING_LOOKUPS = {_('contracts'): '-total_contracts',
                       _('value'): '-total_expended'}
