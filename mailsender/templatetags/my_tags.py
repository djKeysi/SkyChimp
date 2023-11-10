from django import template

register = template.Library()


@register.simple_tag()
def mymedia(value):
    if value:
        return f'/media/{value}'
    else:
        return ''