from django import template
from django.template import defaultfilters
from django.utils.translation import ungettext
from main import settings

register = template.Library()

# A tuple of standard large number to their converters
intword_converters = (
    (3, lambda number: (
        ungettext('%(value).1f thousand', '%(value).1f thousand', number),
        ungettext('%(value)s thousand', '%(value)s thousand', number),
    )),
    (6, lambda number: (
        ungettext('%(value).1f million', '%(value).1f million', number),
        ungettext('%(value)s million', '%(value)s million', number),
    )),
    (9, lambda number: (
        ungettext('%(value).1f billion', '%(value).1f billion', number),
        ungettext('%(value)s billion', '%(value)s billion', number),
    )),
    (12, lambda number: (
        ungettext('%(value).1f trillion', '%(value).1f trillion', number),
        ungettext('%(value)s trillion', '%(value)s trillion', number),
    )),
    (15, lambda number: (
        ungettext('%(value).1f quadrillion', '%(value).1f quadrillion', number),
        ungettext('%(value)s quadrillion', '%(value)s quadrillion', number),
    )),
)

@register.filter(is_safe=False)
def intword(value):
    """
    Converts a large integer to a friendly text representation. Works best
    for numbers over 1 million. For example, 1000000 becomes '1.0 million',
    1200000 becomes '1.2 million' and '1200000000' becomes '1.2 billion'.
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    value /= 100

    if value < 1000:
        return value

    def _check_for_i18n(value, float_formatted, string_formatted):
        """
        Use the i18n enabled defaultfilters.floatformat if possible
        """
        if settings.USE_L10N:
            value = defaultfilters.floatformat(value, 1)
            template = string_formatted
        else:
            template = float_formatted
        return template % {'value': value}

    for exponent, converters in intword_converters:
        large_number = 10 ** exponent
        if value < large_number * 1000:
            new_value = value / float(large_number)
            return _check_for_i18n(new_value, *converters(new_value))
    return value