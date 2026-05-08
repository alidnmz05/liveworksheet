from django import template

register = template.Library()

@register.filter(name='split_choice')
def split_choice(value, arg):
    """
    Splits the string by '/' and returns the item at index arg.
    Usage: {{ question.label|split_choice:0 }}
    """
    try:
        parts = [p.strip() for p in str(value).split('/')]
        return parts[int(arg)]
    except (ValueError, IndexError):
        return ""
