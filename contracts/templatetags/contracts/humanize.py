from django import template
from django.template import defaultfilters
from django.utils.translation import ungettext

register = template.Library()

# A tuple of standard large number to their converters
intword_converters = (
    (0, lambda x: x),
    (3, lambda x: ungettext('%(value)s thousand', '%(value)s thousands', x)),
    (6, lambda x: ungettext('%(value)s million', '%(value)s millions', x)),
    (9, lambda x: ungettext('%(value)s billion', '%(value)s billions', x)),
    (12, lambda x: ungettext('%(value)s trillion', '%(value)s trillions', x)),
)


@register.filter(is_safe=False)
def intword(value):
    """
    Converts a large integer to a friendly text representation.
    For example, 1000000 becomes '1.0 million',
    1200000 becomes '1.2 millions' and '1200000000' becomes '1.2 billions'.
    """
    try:
        value = float(value)
    except TypeError:
        # value is None
        value = 0
    except ValueError:
        # not translated to number
        return value

    value /= 100.  # prices are in cents, we translate them to euros.

    for exponent, converter in intword_converters:
        large_number = 10 ** exponent
        if value < large_number * 1000:
            new_value = value / large_number
            new_value = defaultfilters.floatformat(new_value, 1)
            return converter(new_value) % {'value': new_value}

    # use the highest available
    exponent, converter = intword_converters[-1]
    large_number = 10 ** exponent
    new_value = value / float(large_number)
    new_value = defaultfilters.floatformat(new_value, 1)
    return converter(new_value) % {'value': new_value}
