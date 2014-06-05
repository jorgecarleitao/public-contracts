from django import forms
from django.utils.translation import ugettext as _


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
        return _(field_name)
