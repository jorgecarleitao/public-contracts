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


class ContractSelectorForm(forms.Form):

    search = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control',
                                                           'placeholder': _('filter contracts')})
                             )

    sorting = forms.ChoiceField(required=False,
                                widget=forms.Select(attrs={'class': 'form-control',
                                                           'title': _('order')}),
                                choices=((_('date'), _('date')),
                                         (_('price'), _('price')),
                                         )
                                )

    range = DateRangeField(required=False,
                           widget=forms.TextInput(attrs={'placeholder': _('date range'),
                                                         'class': 'form-control datepicker'}))

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

    def add_prefix(self, field_name):
        if field_name == 'range':
            return _('range')
        return _(field_name)
