from django import template

register = template.Library()

@register.filter(name='split_choice')
def split_choice(value, arg=None):
    """
    Splits the string by '/' and returns the whole list or the item at index arg.
    Usage: {{ question.label|split_choice }} or {{ question.label|split_choice:0 }}
    """
    try:
        parts = [p.strip() for p in str(value).split('/')]
        if arg is None:
            return parts
        return parts[int(arg)]
    except (ValueError, IndexError):
        return "" if arg is not None else []
