from django import template

register = template.Library()

@register.filter
def file_size(value):
    """
    Convert bytes to readable format.
    """
    units = ["B", "KB", "MB", "GB"]

    value = float(value)
    for unit in units:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{value:.2f} GB"
